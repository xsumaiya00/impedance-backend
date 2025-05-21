from idun_guardian_sdk import EEGDevice

def stream_eeg_data():
    device = EEGDevice()
    device.connect()
    device.subscribe("eeg")
    device.subscribe("impedance")

    for packet in device.stream():
        print("EEG:", packet.eeg)
        print("Impedance:", packet.impedance)
        break  # Remove break to keep streaming
