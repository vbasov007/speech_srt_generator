import io
import mp3
import wave

def write_as_mp3(fp, data, sample_rate=24000):
    encoder = mp3.Encoder(fp)
    encoder.set_channels(1)
    encoder.set_bit_rate(64)
    encoder.set_sample_rate(sample_rate)
    encoder.set_quality(2)
    encoder.set_mode(mp3.MODE_SINGLE_CHANNEL)

    encoder.write(data)
    encoder.flush()


def mp3_to_pcm(data: bytes) -> bytes:
    # Convert your data to a file-like object
    read_file = io.BytesIO(data)
    write_file = io.BytesIO()

    decoder = mp3.Decoder(read_file)
    sample_rate = decoder.get_sample_rate()
    nchannels = decoder.get_channels()
    wav_file = wave.Wave_write(write_file)
    wav_file.setnchannels(nchannels)
    wav_file.setsampwidth(2)
    wav_file.setframerate(sample_rate)
    while True:
        pcm_data = decoder.read(4000)
        if not pcm_data:
            break
        else:
            wav_file.writeframes(pcm_data)
    return write_file.getvalue()
