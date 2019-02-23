import argparse
from lsb_encoder import LSBEncoder
from lsb_decoder import LSBDecoder


class Main:
    def __init__(self):
        self.parser = self.create_parser().parse_args()

    @staticmethod
    def create_parser():
        parser = argparse.ArgumentParser(description='LSB')
        parser.add_argument('-en', '--encode', action='store_true',
                            help='if you want to put information into WAV.')
        parser.add_argument('-dec', '--decode', action='store_true',
                            help='if you want to pull out information from WAV.')
        parser.add_argument('-f', '--file', default='', type=str,
                            help='Enter the path to the file'
                                 'you want to inscribe.', nargs='*')
        parser.add_argument('-w', '--wav', default='', type=str,
                            help='Enter the path to the WAV-file', nargs='*')
        return parser

    def main(self):
        if self.parser.encode and self.parser.decode:
            raise Exception("This keys shouldn't be used at the same time")
        if self.parser.encode:
            file_path = ' '.join(self.parser.file)
            wav_path = ' '.join(self.parser.wav)
            if len(file_path) == 0 or len(wav_path) == 0:
                raise Exception('Not all arguments are specified. Try again!')
            lsb = LSBEncoder(file_path, wav_path)
            lsb.inscribe()
            return
        if self.parser.decode:
            wav_path = ' '.join(self.parser.wav)
            if len(wav_path) == 0:
                raise Exception('Not all arguments are specified. Try again!')
            lsb = LSBDecoder(wav_path)
            lsb.get_hidden_information()


if __name__ == '__main__':
    main = Main()
    main.main()
