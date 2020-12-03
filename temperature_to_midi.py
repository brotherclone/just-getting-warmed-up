import csv
from midiutil import MIDIFile

surface_temp_history = "NH.Ts+dSST.csv"  # or your file.
duration_monthly = 1
duration_yearly = duration_monthly * 12
duration_by_decade = duration_yearly * 10


def create_midi(sequence, tempo, volume, file_name, duration=1):
    """

    Takes a sequence of MIDI note numbers and creates a single track MIDI file locally.

    Parameters
    ----------
    duration: int
        note duration in bpm unit
    file_name: str
        desired file name for the midi output
    volume: int
        volume of each note. I usually "humanize" MIDI so I didn't see the need to create different velocities here.
    tempo: int
        BPM of the midi file
    sequence: list
        The sequence of notes, as MIDI values, to write
    """
    track = 0
    channel = 0
    time = 0
    music = MIDIFile(1)
    music.addTempo(track, (time * duration), tempo)
    for pitch in sequence:
        music.addNote(track, channel, pitch, (time * duration), duration, volume)
        time = time + 1
    with open(file_name, "wb") as output_file:
        music.writeFile(output_file)
    print("{file} was created".format(file=file_name))


def convert_sequence(temperatures, increments, midi_note_min=0):
    """

    Takes a list of temperatures and increments, both floats and creates a MIDI equivalent

    temperatures: list
        Temperatures as floats
    increments: list
        A list of segments to compare the temperatures against to get the MIDI notes.
    midi_note_min: int
        The lowest MIDI note used as a basis for sequence creation

    Returns
    ------
    list
        a list of MIDI note numbers

    """
    sequence = []
    for t in temperatures:
        for num, i in enumerate(increments, start=0):
            if t <= i:
                sequence.append(num + midi_note_min)
                break
    print("created {sequence} from {temperatures}".format(sequence=sequence, temperatures=temperatures))
    return sequence


def midi_normalization(csv_values, midi_note_min=0, midi_note_max=127):
    """

    Takes a list of increments based on a min/max MIDI note number.

    Parameters
    ----------
    csv_values: list
        Temperature values from data set
    midi_note_min: int
        Lowest MIDI note you want to use. Usually C2
    midi_note_max: int
        Highest MIDI note you want to use. Usually C8

    Returns
    -------
        list
            A list of floats corresponding to the provide temperature data to create increments
    """
    print("Normalizing sequence {sequence}, for a low note of {low_note} and a high note of {high_note}".format(
        sequence=csv_values, low_note=midi_note_min, high_note=midi_note_max))
    the_range = max(csv_values) - min(csv_values)
    total_midi_notes = midi_note_max - midi_note_min
    increment = the_range / total_midi_notes
    increments = []
    for i in range(midi_note_min, midi_note_max):
        increments.append(min(csv_values) + (i * increment))
    return increments


def read_history(file_name):
    """

    Reads a CSV file.
    #TODO: Hard coded to GIS values. Make this more flexible for other sources as long as it's in monthly averages.

    Parameters
    ----------
        :file_name: str
            The CSV file you wish to read.
    Returns
    -------
        list
            List of temperatures excluding other data.
    """
    print("parsing {file}".format(file=file_name))
    temperatures = []
    with open(file_name, newline='') as csv_file:
        temp_history_reader = csv.reader(csv_file, delimiter=',', quotechar='|')
        for row_number, row in enumerate(temp_history_reader, start=0):
            if row_number > 1:
                for column_number, column in enumerate(row, start=0):
                    if 1 <= column_number < 14:
                        if column != "***":
                            temperatures.append(float(column))
    return temperatures


def get_list_average(list_to_average):
    """

    Averages list

    Parameters
    ----------
    list_to_average: list
        List of numbers to average

    Returns
    -------
        int
           Average of values in list
    """
    return sum(list_to_average) / len(list_to_average)


def step_average(sequence, step):
    """

    Creates a shorter, average list of numbers based on the desired steps

    Parameters
    ----------
        sequence: list
            List of integers or floats
        step: int
            The number of steps you wish to average. E.g. [1,2,3,4,5,6,7,8] with a step of 4 would return [10,24]
    Returns
    -------
        list
            The stepped list result
    """
    stepped_sequence = []
    step_sequence = []
    for sequence_number, sequence_item in enumerate(sequence, start=0):
        if sequence_number % step == 0 and sequence_number != 0:
            average = get_list_average(step_sequence)
            stepped_sequence.append(average)
            step_sequence = []
        step_sequence.append(sequence_item)
    return stepped_sequence


def create_monthly_sequence(temperature_data, output_midi_file_name, bpm, volume, midi_note_min, midi_note_max):
    """

    Creates a MIDI file with one note per month.

    Parameters
    ----------
    temperature_data: string
        Name of the local data set in CSV.
    output_midi_file_name: str
        What you wish to name the file
    bpm: int
        Beats per minute to render the MIDI at
    volume: int
        MIDI Volume, 0-127
    midi_note_min: int
        Lowest MIDI note you want to use. Usually C2
    midi_note_max: int
        Highest MIDI note you want to use. Usually C8
    """
    print("creating monthly sequence")
    temperature_history = read_history(temperature_data)
    new_increments = midi_normalization(temperature_history, midi_note_min, midi_note_max)
    sequence = convert_sequence(temperature_history, new_increments, midi_note_min)
    create_midi(sequence, bpm, volume, "{filename}_monthly.mid".format(filename=output_midi_file_name),
                duration_monthly)


def create_yearly_sequence(temperature_data, output_midi_file_name, bpm, volume, midi_note_min, midi_note_max):
    """

    Creates a MIDI file with one note per year.

    Parameters
    ----------
    temperature_data: string
        Name of the local data set in CSV.
    output_midi_file_name: str
        What you wish to name the file
    bpm: int
        Beats per minute to render the MIDI at
    volume: int
        MIDI Volume, 0-127
    midi_note_min: int
        Lowest MIDI note you want to use. Usually C2
    midi_note_max: int
        Highest MIDI note you want to use. Usually C8
    """
    print("creating yearly sequence")
    temperature_history = read_history(temperature_data)
    yearly_history = step_average(temperature_history, duration_yearly)
    new_increments = midi_normalization(yearly_history, midi_note_min, midi_note_max)
    sequence = convert_sequence(yearly_history, new_increments, midi_note_min)
    create_midi(sequence, bpm, volume, "{filename}_yearly.mid".format(filename=output_midi_file_name), duration_yearly)


def create_decade_sequence(temperature_data, output_midi_file_name, bpm, volume, midi_note_min, midi_note_max):
    """

    Creates a MIDI file with one note per decade. Good for bass or drones.

    Parameters
    ----------
    temperature_data: string
        Name of the local data set in CSV.
    output_midi_file_name: str
        What you wish to name the file
    bpm: int
        Beats per minute to render the MIDI at
    volume: int
        MIDI Volume, 0-127
    midi_note_min: int
        Lowest MIDI note you want to use. Usually C2
    midi_note_max: int
        Highest MIDI note you want to use. Usually C8
    """
    print("creating decade by decade sequence")
    temperature_history = read_history(temperature_data)
    decade_history = step_average(temperature_history, duration_by_decade)
    new_increments = midi_normalization(decade_history, midi_note_min, midi_note_max)
    sequence = convert_sequence(decade_history, new_increments, midi_note_min)
    create_midi(sequence, bpm, volume, "{filename}_decade.mid".format(filename=output_midi_file_name),
                duration_by_decade)


def create_all_sequences(temperature_data, output_midi_file_name, bpm, volume, midi_note_min, midi_note_max):
    """

    Creates three MIDI files with notes per month, year, and decade.

    Parameters
    ----------
    temperature_data: string
        Name of the local data set in CSV.
    output_midi_file_name: str
        What you wish to name the file
    bpm: int
        Beats per minute to render the MIDI at
    volume: int
        MIDI Volume, 0-127
    midi_note_min: int
        Lowest MIDI note you want to use. Usually C2
    midi_note_max: int
        Highest MIDI note you want to use. Usually C8
    """
    print("creating all sequences:")
    create_monthly_sequence(temperature_data, output_midi_file_name, bpm, volume, midi_note_min, midi_note_max)
    create_yearly_sequence(temperature_data, output_midi_file_name, bpm, volume, midi_note_min, midi_note_max)
    create_decade_sequence(temperature_data, output_midi_file_name, bpm, volume, midi_note_min, midi_note_max)


def set_mode(mode, temperature_data, output_midi_file_name="just_warming_up", bpm=120, volume=100, midi_note_min=0,
             midi_note_max=127):
    """

    Triggers the desired function

    Parameters
    ----------
    mode: int
        mode_switch number - 0 => monthly, 1 => yearly, 2 => by decade, 3 => Make all three
    temperature_data: string
        Name of the local data set in CSV.
    output_midi_file_name: str
        What you wish to name the file
    bpm: int
        Beats per minute to render the MIDI at
    volume: int
        MIDI Volume, 0-127
    midi_note_min: int
        Lowest MIDI note you want to use. Usually C2
    midi_note_max: int
        Highest MIDI note you want to use. Usually C8
    Returns
    -------
        function
            Runs the function associated with the desired mode.
    """
    func = mode_switch.get(mode, "invalid mode")
    print("performing {requested_mode}".format(requested_mode=mode))
    return func(temperature_data, output_midi_file_name, bpm, volume, midi_note_min, midi_note_max)


mode_switch = {
    0: create_monthly_sequence,
    1: create_yearly_sequence,
    2: create_decade_sequence,
    3: create_all_sequences
}

if __name__ == "__main__":
    set_mode(3, surface_temp_history, "just_warming_up", 160, 112, 24, 96)
