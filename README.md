# Tilt Sensor Logger

WitMotion 9軸IMUセンサー用データ収集システム

## 概要
このプロジェクトは、WitMotion 9軸IMUセンサー（加速度、角速度、磁場、姿勢角）からデータを収集し、時系列ファイルに記録するシステムです。

## システム構成

```
WitMotionセンサー → Modbus/RS485 → device_model.py → sensor_logger.py → データファイル
```

## ファイル構成
- `logger_base/` - データ収集・処理・制御フレームワーク
- `device_model.py` - WitMotionセンサー通信ライブラリ
- `sensor_logger.py` - センサーデータロガー
- `test.py` - 基本動作テスト用スクリプト

## 取得データ

- **加速度**: AccX, AccY, AccZ [g] (±2g範囲設定時の分解能は0.0000039g/LSB)
- **角速度**: AsX, AsY, AsZ [°/s] (±2000°/s範囲設定時の分解能は0.061°/s/LSB)  
- **磁場**: HX, HY, HZ [Gauss]
- **姿勢角**: AngX(Roll), AngY(Pitch) [°] (傾斜角度の測定精度は0.001°)
- **方位角**: AngZ(Yaw/Heading) [°] (精度は0.1°)

## 使用方法

### 基本的な使用

```bash
# センサーデータの連続記録開始
python3 sensor_logger.py

# 基本動作テスト
python3 test.py
```

## 出力ファイル

データは以下の形式で保存されます：
- パス: `./data/witsensor/年/月/日_witsensor.raw`
- フォーマット: タイムスタンプ + 12チャンネルのセンサーデータ

## 動作環境

- **OS**: Linux (Raspberry Pi推奨)
- **Python**: 3.6+
- **接続**: USB-RS485変換器経由でセンサー接続

## 依存関係

```bash
pip install pyserial python-dateutil
```

## ハードウェア設定

- **デバイス**: `/dev/ttyUSB0`
- **ボーレート**: 9600 bps
- **プロトコル**: Modbus RTU
- **デバイスID**: 0x50