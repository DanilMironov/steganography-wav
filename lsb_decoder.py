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

    def read_the_flag(self, bytes_to_describe, index, offset):
        description = ''
        for i in range(bytes_to_describe):  # считаем длину содержимого
            current_byte = self.main_file[index: index + 1]
            bin_repr_current_byte = Stuff.get_bin_str_from_bytearray(current_byte)
            list_of_current_chars = list(bin_repr_current_byte)
            description += list_of_current_chars[-1]
            index += offset
        return index, description

    def read_the_content(self, buffer, length, index, offset):
        string_repr = ''
        buffer_index = 0
        for i in range(length):
            current_byte = self.main_file[index: index + 1]
            bin_repr_current_byte = Stuff.get_bin_str_from_bytearray(current_byte)
            current_pairs = Stuff.split_in_two_bits(bin_repr_current_byte)
            string_repr += current_pairs[-1]
            if len(string_repr) == 8:
                buffer[buffer_index] = Stuff.get_int_from_bin(string_repr)
                string_repr = ''
                buffer_index += 1
            index += offset
        return index

    def read_the_hash(self, length_of_hash, index, offset):
        hash_str = ''
        for i in range(length_of_hash):  # считываем хеш
            current_byte = self.main_file[index: index + 1]
            bin_repr_current_byte = Stuff.get_bin_str_from_bytearray(current_byte)
            current_pairs = Stuff.split_in_two_bits(bin_repr_current_byte)
            hash_str += current_pairs[-1]
            index += offset
        rec_hash = Stuff.get_int_from_bin(hash_str)
        return index, rec_hash

    def get_hidden_information(self):
        offset = bytes_per_sample = self.bits_per_sample // 8
        index = self.index_of_start_of_data + bytes_per_sample  # индекс первого байта
        bytes_to_describe_length = 32
        index, length_description = self.read_the_flag(
            bytes_to_describe_length,
            index,
            offset
        )
        length = Stuff.get_int_from_bin(length_description)
        length_of_new_bytearray = length // 4
        bytes_to_describe_length_of_name = 16
        index, length_of_name_description = self.read_the_flag(
            bytes_to_describe_length_of_name,
            index,
            offset
        )
        length_of_name = Stuff.get_int_from_bin(length_of_name_description)
        length_of_name_array = length_of_name // 4
        bytes_to_describe_hash = 8
        index, length_of_hash_description = self.read_the_flag(
            bytes_to_describe_hash,
            index,
            offset
        )
        length_of_hash = Stuff.get_int_from_bin(length_of_hash_description)  # длина хеша
        index, rec_hash = self.read_the_hash(length_of_hash, index, offset)
        name_bytearray = bytearray(length_of_name_array)
        index = self.read_the_content(name_bytearray, length_of_name, index, offset)
        name_of_recieved = name_bytearray.decode()
        content_of_recieved = bytearray(length_of_new_bytearray)
        self.read_the_content(content_of_recieved, length, index, offset)
        actually_hash = Stuff.get_hash(content_of_recieved)
        if rec_hash != actually_hash:
            raise Exception('There was a distortion of information')
        with open('(recieved) ' + name_of_recieved, 'wb') as file:
            file.write(content_of_recieved)


if __name__ == '__main__':
    dec = LSBDecoder('new_wav.wav')
    dec.get_hidden_information()
