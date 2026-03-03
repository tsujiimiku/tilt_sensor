#!/usr/bin/env python3
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
import glob
import time
from logger_base.logger import Logger_base
from os.path import dirname, abspath, join


# パラメータ設定
input_pattern = '/home/gb/logger/data/witsensor/*/*/*.raw'
delta_alpha_deg = 0.001
delta_beta_deg = 0.001
time_interval = 60  # 60秒間隔でチェック
time_diff_threshold = 50  # 50秒以上の差があれば更新
lockfile = join(dirname(abspath(__file__)), '.logger_angle_processor.lock')
sockfile = join(dirname(abspath(__file__)), '.logger_angle_processor.sock')

def sensor_angle(ang_alpha, ang_beta):
    """
    Calculate sensor angle (vectorized)
    
    Parameters:
    -----------
    ang_alpha : numpy.ndarray
        Sensor alpha angle (radians)
    ang_beta : numpy.ndarray
        Sensor beta angle (radians)
    
    Returns:
    --------
    numpy.ndarray
        Calculated sensor angle (radians)
    """
    y = np.sin(ang_alpha)
    x = np.sin(ang_beta)
    angle = np.arctan2(y, x)
    return angle

def calculate_error_propagation(alpha, beta, delta_alpha, delta_beta):
    """
    Calculate error propagation (vectorized)
    
    Parameters:
    -----------
    alpha : numpy.ndarray
        Sensor alpha angle (radians)
    beta : numpy.ndarray
        Sensor beta angle (radians)
    delta_alpha : float
        Alpha angle error (radians)
    delta_beta : float
        Beta angle error (radians)
    
    Returns:
    --------
    numpy.ndarray
        Calculated error propagation (radians)
    """
    # Calculate partial derivatives (vectorized)
    denominator = np.sin(beta)**2 + np.sin(alpha)**2
    d_angle_d_alpha = np.abs(np.cos(alpha) * np.sin(beta)) / denominator
    d_angle_d_beta = np.abs(-np.sin(alpha) * np.cos(beta)) / denominator
    error = np.sqrt(d_angle_d_alpha**2 * delta_alpha**2 + d_angle_d_beta**2 * delta_beta**2)
    
    return error

def read_sensor_data(filepath):
    """
    Read sensor data file
    
    Parameters:
    -----------
    filepath : str
        Path to data file
    
    Returns:
    --------
    pandas.DataFrame
        Loaded data
    """
    # Skip header lines and read data
    column_names = ['Localtime', 'Unixtime', 
                    'AccX', 'AccY', 'AccZ',
                    'AsX', 'AsY', 'AsZ',
                    'HX', 'HY', 'HZ',
                    'AngX', 'AngY', 'AngZ']
    
    df = pd.read_csv(filepath, 
                     delim_whitespace=True, 
                     comment='#',
                     names=column_names,
                     skip_blank_lines=True)
    
    return df

def calculate_angles_and_errors(df, delta_alpha_deg=0.001, delta_beta_deg=0.001):
    """
    Calculate angles and errors for the entire DataFrame (vectorized)
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Input sensor data
    delta_alpha_deg : float
        Alpha angle error (degrees)
    delta_beta_deg : float
        Beta angle error (degrees)
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with calculated angles and errors
    """
    # Use AngX and AngY (assuming recorded in degrees)
    ang_alpha_deg = df['AngX'].values
    ang_beta_deg = df['AngY'].values
    
    # Convert to radians (vectorized)
    ang_alpha_rad = np.deg2rad(ang_alpha_deg)
    ang_beta_rad = np.deg2rad(ang_beta_deg)
    delta_alpha_rad = np.deg2rad(delta_alpha_deg)
    delta_beta_rad = np.deg2rad(delta_beta_deg)
    
    # Calculate angles and errors (vectorized)
    calculated_angles_rad = sensor_angle(ang_alpha_rad, ang_beta_rad)
    calculated_errors_rad = calculate_error_propagation(
        ang_alpha_rad, ang_beta_rad, delta_alpha_rad, delta_beta_rad
    )
    
    # Convert to degrees (vectorized)
    calculated_angles_deg = np.rad2deg(calculated_angles_rad)
    calculated_errors_deg = np.rad2deg(calculated_errors_rad)
    
    # Store results in DataFrame
    result_df = pd.DataFrame({
        'Localtime': df['Localtime'],
        'Unixtime': df['Unixtime'],
        'AngX_deg': ang_alpha_deg,
        'AngY_deg': ang_beta_deg,
        'Calculated_Angle_deg': calculated_angles_deg,
        'Error_deg': calculated_errors_deg
    })
    
    return result_df

def get_output_filepath(input_file):
    """
    Get output file path in the same directory as input file
    
    Parameters:
    -----------
    input_file : str
        Input file path
    
    Returns:
    --------
    Path
        Output file path
    """
    input_path = Path(input_file)
    output_file = input_path.parent / f"{input_path.stem}_angles.csv"
    return output_file

def process_sensor_data_full(input_file, delta_alpha_deg=0.001, delta_beta_deg=0.001):
    """
    Process entire sensor data file and create new output file
    
    Parameters:
    -----------
    input_file : str
        Input file path
    delta_alpha_deg : float
        Alpha angle error (degrees)
    delta_beta_deg : float
        Beta angle error (degrees)
    
    Returns:
    --------
    str
        Output file path
    """
    print(f"Processing full file: {input_file}")
    
    # Read data
    df = read_sensor_data(input_file)
    
    # Calculate angles and errors (vectorized)
    result_df = calculate_angles_and_errors(df, delta_alpha_deg, delta_beta_deg)
    
    # Get output file path
    output_file = get_output_filepath(input_file)
    
    # Output to CSV
    result_df.to_csv(output_file, index=False)
    print(f"Created new file: {output_file}")
    print(f"Number of processed data points: {len(result_df)}")
    
    return str(output_file)

def process_sensor_data_incremental(input_file, output_file, delta_alpha_deg=0.001, delta_beta_deg=0.001):
    """
    Process only new data and append to existing output file
    
    Parameters:
    -----------
    input_file : str
        Input file path
    output_file : Path
        Output file path
    delta_alpha_deg : float
        Alpha angle error (degrees)
    delta_beta_deg : float
        Beta angle error (degrees)
    
    Returns:
    --------
    int
        Number of new data points added
    """
    # Read existing output file
    existing_df = pd.read_csv(output_file)
    last_unixtime = existing_df['Unixtime'].iloc[-1]
    
    # Read input data
    input_df = read_sensor_data(input_file)
    
    # Filter new data (unixtime > last_unixtime)
    new_data_df = input_df[input_df['Unixtime'] > last_unixtime].copy()
    
    if len(new_data_df) == 0:
        print("No new data to process.")
        return 0
    
    print(f"Processing {len(new_data_df)} new data points")
    
    # Calculate angles and errors for new data only (vectorized)
    new_result_df = calculate_angles_and_errors(new_data_df, delta_alpha_deg, delta_beta_deg)
    
    # Append to existing file
    new_result_df.to_csv(output_file, mode='a', header=False, index=False)
    print(f"Appended {len(new_result_df)} new data points to {output_file}")
    
    return len(new_result_df)





class LoggerAngleProcessor(Logger_base):
    def __init__(self, input_pattern, delta_alpha_deg, delta_beta_deg, 
                 time_diff_threshold, lock_file, sock_file, interval_sec):
        """
        Initialize LoggerAngleProcessor
        
        Parameters:
        -----------
        input_pattern : str
            Input file pattern (e.g., '/home/gb/logger/data/witsensor/*/*.raw')
        delta_alpha_deg : float
            Alpha angle error (degrees)
        delta_beta_deg : float
            Beta angle error (degrees)
        time_diff_threshold : float
            Time difference threshold in seconds (default: 50)
        lock_file : str
            Lock file path
        sock_file : str
            Socket file path
        interval_sec : float
            Sleep interval between checks (seconds)
        """
        # Logger_baseの初期化（output_file_pathとfile_headerは不要）
        super().__init__(output_file_path=None,
                         file_header=None,
                         lock_file=lock_file,
                         sock_file=sock_file,
                         interval_sec=interval_sec)
        
        self.input_pattern = input_pattern
        self.delta_alpha_deg = delta_alpha_deg
        self.delta_beta_deg = delta_beta_deg
        self.time_diff_threshold = time_diff_threshold
    
    def initialize(self):
        """初期化処理"""
        print(f"Started monitoring: {self.input_pattern}")
        print(f"Output files will be saved in the same directory as input files")
        print(f"Time difference threshold: {self.time_diff_threshold} seconds")
    
    def do(self):
        """定期的に実行される処理"""
        # ソケットからメッセージを受信（interval変更用）
        msg = self.sock_recv()
        if msg is not None:
            try:
                parts = msg.split()
                if len(parts) == 1:
                    # intervalのみ指定
                    self.set_interval(float(parts[0]))
                elif len(parts) == 2:
                    # intervalとthreshold両方指定
                    self.set_interval(float(parts[0]))
                    self.time_diff_threshold = float(parts[1])
                    print(f"Updated time_diff_threshold to {self.time_diff_threshold} seconds")
            except Exception as e:
                print(f"Error parsing socket message: {e}")
        
        try:
            # ファイル検索
            files = glob.glob(self.input_pattern)
            files.sort()
            
            if len(files) == 0:
                print(f"No files found matching pattern: {self.input_pattern}")
                return
            
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
            print(f"Found {len(files)} files to check")
            
            # 出力ファイルが存在しないファイルを処理
            for input_file in files:
                output_file = get_output_filepath(input_file)
                if not output_file.exists():
                    print(f"Output file not found: {output_file}")
                    process_sensor_data_full(input_file, self.delta_alpha_deg, self.delta_beta_deg)
            
            # 最後のファイルの更新チェック
            input_file = files[-1]
            output_file = get_output_filepath(input_file)
            
            if not output_file.exists():
                print(f"Output file not yet created: {output_file}")
                return
            
            # 既存の出力ファイルを読み込み
            existing_df = pd.read_csv(output_file)
            last_unixtime = existing_df['Unixtime'].iloc[-1]
            
            # 入力データを読み込み
            input_df = read_sensor_data(input_file)
            input_last_unixtime = input_df['Unixtime'].iloc[-1]
            
            # 時間差をチェック
            time_diff = input_last_unixtime - last_unixtime
            
            if time_diff < self.time_diff_threshold:
                print(f"\nFile: {Path(input_file).name}")
                print(f"Time difference is {time_diff:.1f} seconds (< {self.time_diff_threshold}s). No update needed.")
            else:
                print(f"\nFile: {Path(input_file).name}")
                print(f"Time difference is {time_diff:.1f} seconds (>= {self.time_diff_threshold}s). Updating...")
                process_sensor_data_incremental(
                    input_file, output_file, self.delta_alpha_deg, self.delta_beta_deg
                )
        
        except Exception as e:
            print(f"An error occurred in do(): {e}")
    
    def finalize(self):
        """終了処理"""
        print("\nStopping angle processor.")


if __name__ == '__main__':
    logger = LoggerAngleProcessor(
        input_pattern=input_pattern,
        delta_alpha_deg=delta_alpha_deg,
        delta_beta_deg=delta_beta_deg,
        time_diff_threshold=time_diff_threshold,
        lock_file=lockfile,
        sock_file=sockfile,
        interval_sec=time_interval
    )
    logger.run(isDebug=False)