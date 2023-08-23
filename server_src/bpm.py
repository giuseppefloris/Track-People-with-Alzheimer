def bpm_operations(msg):
    print("BPM OPERATIONS\n")
    print(msg.payload)
    with open('bpm_data.txt', 'wb') as f:
        f.write(msg.payload)
