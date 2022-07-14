from numpy import array, double

def extract_data_segment_secs(data, start_sec, end_sec):
# function to extract data segments between given times in seconds
    data_ex = {}
    for key in data.keys():
        data_ex[key] = []
    for it, time in enumerate(data['seconds']):
        if time >= start_sec:
            if time <= end_sec:
                for key in data.keys():
                    data_ex[key].append(data[key][it])
            else:
                break
    for key in data.keys():
        if key != 'timestamp':
            data_ex[key] = array(data_ex[key], dtype = double)

    return data_ex

def extract_data_segment_time(data, start_time, end_time):
# function to extract data segments between given timestamps
    data_ex = {}
    for key in data.keys():
        data_ex[key] = []
    for it, time in enumerate(data['timestamp']):
        if time >= start_time:
            if time <= end_time:
                for key in data.keys():
                    data_ex[key].append(data[key][it])
            else:
                break
    for key in data.keys():
        if key != 'timestamp':
            data_ex[key] = array(data_ex[key], dtype = double)

    return data_ex
