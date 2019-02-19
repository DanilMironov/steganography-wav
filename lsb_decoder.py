class LSBDecoder:
    def __init__(self, path_to_the_file):
        self.main_file = self._read_the_file(path_to_the_file)
        self.index_of_start_of_data = \
            self._find_index_of_the_start_of_data(self.main_file)
        self.bits_per_sample = self._get_bits_per_sample()

    @staticmethod
    def _read_the_file(path_to_the_file):
        with open(path_to_the_file, 'rb') as file:
            data = bytearray(file.read())
        return data

    @staticmethod
    def _split_in_two_bits(string):
        list_of_pair = []
        for i in range(len(string) // 2):
            list_of_pair.append(string[2 * i:2 * i + 2])
        return list_of_pair

    @staticmethod
    def _find_index_of_the_start_of_data(list_of_bytes: bytearray):
        offset = 8
        res = list_of_bytes.find(b'data')
        return res + offset

    def _get_bits_per_sample(self):
        byte34 = self.main_file[34].to_bytes(1, 'little')
        byte35 = self.main_file[35].to_bytes(1, 'little')
        bits_per_sample = int.from_bytes(byte34 + byte35, 'little')
        return bits_per_sample

    @staticmethod
    def _get_int_from_bin(bin_str):
        return int(bin_str, 2)

    @staticmethod
    def _get_bin_str_from_bytearray(data: bytearray):
        bin_str = ''.join('{}'.format(bin(e)[2:]) for e in data)
        while len(bin_str) % 8 != 0:
            bin_str = '0' + bin_str
        return bin_str

    def get_hidden_information(self):
        bytes_to_describe_length = 32
        offset = bytes_per_sample = self.bits_per_sample // 8
        index = self.index_of_start_of_data + bytes_per_sample - 1  # индекс первого байта
        length_description = ''
        for i in range(bytes_to_describe_length):
            current_byte = self.main_file[index: index + 1]
            bin_repr_current_byte = self._get_bin_str_from_bytearray(current_byte)
            list_of_current_chars = list(bin_repr_current_byte)
            length_description += list_of_current_chars[-1]
            index += offset
        length = self._get_int_from_bin(length_description)
        length_of_new_bytearray = length // 4
        recieved = bytearray(length_of_new_bytearray)
        rec_str = ''
        bytearray_index = 0
        for i in range(length):
            current_byte = self.main_file[index: index + 1]
            bin_repr_current_byte = self._get_bin_str_from_bytearray(current_byte)
            current_pairs = self._split_in_two_bits(bin_repr_current_byte)
            rec_str += current_pairs[-1]
            if len(rec_str) == 8:
                recieved[bytearray_index] = self._get_int_from_bin(rec_str)
                rec_str = ''
                bytearray_index += 1
            index += offset
        with open('rec.txt', 'wb') as file:
            file.write(recieved)


if __name__ == '__main__':
    dec = LSBDecoder('new_wav.wav')
    dec.get_hidden_information()
