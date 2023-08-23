def acc_operations(msg):
    print("ACCELEROMETER OPERATIONS\n")
    print(msg.payload)
    with open('acc_data.txt', 'wb') as f:
        f.write(msg.payload)
