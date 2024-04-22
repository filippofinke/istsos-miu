import csv
import random
from isodate import parse_duration

def generate_observation_data(id_num, obs, datastream_start_id, data_stream_num, feature_num, start_datetime, timestep):
    data = []
    start_datetime_str = start_datetime
    timestep_str = timestep

    # Parse the start datetime and timestep duration using iso8601
    start_datetime = start_datetime_str
    timestep_duration = parse_duration(timestep_str)
    
    # Generate timestamps using the specified timestep
    current_time = start_datetime
    id = id_num - 1

    for j in range(0, data_stream_num):
        
        for i in range(0, obs):
            id = id + 1
            timestamps = current_time.isoformat()
            current_time += timestep_duration
            phenomenonTime = timestamps
            resultTime = timestamps
            resultType = random.randint(0, 4)
            if resultType == 0:
                resultString = "testvalue"
                resultInteger = "None"
                resultDouble = "None"
                resultBoolean = "None"
                resultJSON = "None"
            elif resultType == 1:
                resultInteger = random.randint(1, 100)
                resultString = "None"
                resultDouble = "None"
                resultBoolean = "None"
                resultJSON = "None"
            elif resultType == 2:
                resultDouble = random.random()
                resultString = "None"
                resultInteger = "None"
                resultBoolean = "None"
                resultJSON = "None"
            elif resultType == 3:
                resultString = "None"
                resultInteger = "None"
                resultDouble = "None"
                resultJSON = "None"
                resultBoolean = random.choice([True, False])
            elif resultType == 4:
                resultJSON = f'{{"testvalue": "value-{resultType}"}}'
                resultString = "None"
                resultInteger = "None"
                resultDouble = "None"
                resultBoolean = "None"
            parameters = f"{{}}"       
            resultQuality ="None"
            validTime = "None"
            datastream_id = datastream_start_id
            feature_of_interest_id =random.randint(1, feature_num)

            # Append the row to the data list
            data.append([id, phenomenonTime,resultTime, resultType, resultString, resultInteger, resultDouble, resultBoolean, resultJSON, resultQuality, validTime, parameters, datastream_id, feature_of_interest_id])
        datastream_start_id = datastream_start_id + 1


    print("creating Observation data...")
    # Write the data to a CSV file
    with open('data/Observation.csv', 'w', newline = '') as file:
        writer = csv.writer(file)
        writer.writerow(["id", "phenomenonTime", "resultTime", "resultType", "resultString", "resultInteger", "resultDouble", "resultBoolean", "resultJSON", "resultQuality", "validTime", "parameters", "datastream_id", "feature_of_interest_id"])
        writer.writerows(data)