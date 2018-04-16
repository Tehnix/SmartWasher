import replay_data


def main():
    noiseValues = replay_data.get_noise_values()
    audioSamples = replay_data.get_audio_samples()
    step = 0
    while True:
        if (step + 1) * 200 > 2400:
            step = 0
        print("Choose an action:")
        print("    1: Simulate silent state")
        print("    2: Simulate running state")
        print("    3: Simulate running state with steps")
        print("    4: Reset steps")
        print("    q: quit")
        action = input(">> ")
        if action == "1":
            print("Adding silent data")
            replay_data.add_silent_values(noiseValues)
        elif action == "2":
            print("Adding running data")
            replay_data.add_running_values(audioSamples, 0)
        elif action == "3":
            print("Adding running data at step {0}".format(step))
            replay_data.add_running_values(audioSamples, step)
            step += 1
        elif action == "4":
            step = 0
        elif action == "q":
            break
        else:
            print("Invalid action!")

if __name__ == '__main__':
    main()
