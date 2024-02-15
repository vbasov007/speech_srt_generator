
import mp3

def write_as_mp3(fp, data):
    encoder = mp3.Encoder(fp)
    encoder.set_channels(1)
    encoder.set_bit_rate(64)
    encoder.set_sample_rate(16000)
    encoder.set_mode(mp3.MODE_SINGLE_CHANNEL)

    encoder.write(data)
    encoder.flush()