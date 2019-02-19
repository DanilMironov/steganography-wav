from lsb_stuff import LSBStuff as Stuff


class LSBDecoder:
    def __init__(self, path_to_the_file):
        self.main_file = Stuff.read_the_file(path_to_the_file)
        self.index_of_start_of_data = \
            Stuff.find_index_of_the_start_of_data(self.main_file)
        self.bits_per_sample = self._get_bits_per_sample()

    def _get_bits_per_sample(self):
        byte34 = self.main_file[34].to_bytes(1, 'little')
        byte35 = self.main_file[35].to_bytes(1, 'little')
        bits_per_sample = int.from_bytes(byte34 + byte35, 'little')
        return bits_per_sample

    def get_hidden_information(self):
        bytes_to_describe_length = 32
        offset = bytes_per_sample = self.bits_per_sample // 8
        index = self.index_of_start_of_data + bytes_per_sample - 1  # индекс первого байта
        length_description = ''
        for i in range(bytes_to_describe_length):
            current_byte = self.main_file[index: index + 1]
            bin_repr_current_byte = Stuff.get_bin_str_from_bytearray(current_byte)
            list_of_current_chars = list(bin_repr_current_byte)
            length_description += list_of_current_chars[-1]
            index += offset
        length = Stuff.get_int_from_bin(length_description)
        length_of_new_bytearray = length // 4
        content_of_recieved = bytearray(length_of_new_bytearray)
        rec_str = ''
        bytearray_index = 0
        bytes_to_describe_length_of_name = 16
        length_of_name_description = ''
        for i in range(bytes_to_describe_length_of_name):
            current_byte = self.main_file[index: index + 1]
            bin_repr_current_byte = Stuff.get_bin_str_from_bytearray(current_byte)
            list_of_current_chars = list(bin_repr_current_byte)
            length_of_name_description += list_of_current_chars[-1]
            index += offset
        length_of_name = Stuff.get_int_from_bin(length_of_name_description)
        length_of_name_array = length_of_name // 4
        name_bytearray = bytearray(length_of_name_array)
        name_str = ''
        name_bytearray_index = 0
        for i in range(length_of_name):
            current_byte = self.main_file[index: index + 1]
            bin_repr_current_byte = Stuff.get_bin_str_from_bytearray(current_byte)
            current_pairs = Stuff.split_in_two_bits(bin_repr_current_byte)
            name_str += current_pairs[-1]
            if len(name_str) == 8:
                name_bytearray[name_bytearray_index] = Stuff.get_int_from_bin(name_str)
                name_str = ''
                name_bytearray_index += 1
            index += offset
        name_of_recieved = name_bytearray.decode()
        for i in range(length):
            current_byte = self.main_file[index: index + 1]
            bin_repr_current_byte = Stuff.get_bin_str_from_bytearray(current_byte)
            current_pairs = Stuff.split_in_two_bits(bin_repr_current_byte)
            rec_str += current_pairs[-1]
            if len(rec_str) == 8:
                content_of_recieved[bytearray_index] = Stuff.get_int_from_bin(rec_str)
                rec_str = ''
                bytearray_index += 1
            index += offset
        with open('recieved ' + name_of_recieved, 'wb') as file:
            file.write(content_of_recieved)


if __name__ == '__main__':
    dec = LSBDecoder('new_wav.wav')
    dec.get_hidden_information()
