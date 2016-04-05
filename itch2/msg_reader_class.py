from msg_action_structs import *

class MsgReader(object):
    """
    A message reader class
    """
    def __init__(self):
        pass

    def set_path(self, files_path):
        """
        set file paths

        Args:
            files_path: list of files address
        Returns:
            return False if files_path contains no file
        """
        self.binary_files_path = files_path # may be a list if multiple files
        self.total_files_num = len(files_path)
        if self.total_files_num == 0:
            print "The input file list has no element inside.\n"
            return False
        else:
            self.file_iter = iter(self.binary_files_path) # iterator

    def read_next_file_in_list(self):
        """
        Read next file in files_path list

        Args:
            None
        Returns:
            return False if no next file, and close the current open file. else return True.
        """
        self.cur_file_path = next(self.file_iter, None)
        if self.cur_file_path is None:
            self.cur_file.close()
            return False
        self.cur_file = open(self.cur_file_path, 'rb')
        return True

    def fetch_one(self, focus_only_stock = False):
        """
        fetch next message in the current opened file

        Args:
            focus_only_stock: bool. if only parse those stock related messages
        Returns:
            return -1 if cant read any more, return message struct else. return None if the mtype is not stock related.
        """

        # TODO: return type here is really... ugly; need fix.
        msg_length_bin = self.cur_file.read(2)
        if msg_length_bin is None or len(msg_length_bin)<2:
            return -1 # should read_next_file_in_list
        msg_length = unpack('!H', msg_length_bin)[0]
        msg_bin = self.cur_file.read(msg_length)
        if msg_bin is None or len(msg_bin)<msg_length:
            return -1 # should read_next_file_in_list
        return parse(msg_bin, focus_only_stock=focus_only_stock)