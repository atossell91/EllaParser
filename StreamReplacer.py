CHUNK_LEN = 4096
MAX_LABEL_LEN = 256
MAX_TAG_LEN = 64

TAG_START = b"{{"
TAG_END = b"}}"


def replace_text(infile, outfile, label_func, label_func_args=None):            
    current_state = 1

    label_buffer = bytearray(MAX_LABEL_LEN)
    label_buffer_cursor = 0

    tag_buffer = bytearray(MAX_TAG_LEN)
    tag_buffer_cursor = 0

    write_buffer = bytearray(CHUNK_LEN)
    write_buffer_cursor = 0

    tag_cursor = 0
    
    while True:
        data = infile.read(CHUNK_LEN)

        if not data:
            break

        i = 0
        while i < len(data):

            if write_buffer_cursor > CHUNK_LEN-MAX_LABEL_LEN-MAX_TAG_LEN*2:
                outfile.write(write_buffer[0: write_buffer_cursor])
                write_buffer_cursor = 0

            c = data[i]

            if current_state & 1 > 0:
                # NoTag state
                #print(f"State (1), index {i}")
                if c == TAG_START[0]:
                    current_state = 4
                else:
                    write_buffer[write_buffer_cursor] = c #### Do we check write buffer index against length? Flushing the write buffer??
                    write_buffer_cursor =  write_buffer_cursor + 1
                    i = i + 1
            elif current_state & 2 > 0:
                #print(f"State (2), index {i}")
                # Label state
                if c == TAG_END[0]:
                    current_state = 8
                else:
                    label_buffer[label_buffer_cursor] = c
                    label_buffer_cursor = label_buffer_cursor + 1 #### Need to check label value in dict
                    i = i + 1
            elif current_state & 4 > 0:
                #print(f"State (4), index {i}")
                # Potential start tag state
                if c == TAG_START[tag_cursor]:
                    tag_buffer[tag_buffer_cursor] = c
                    tag_cursor = tag_cursor + 1
                    i = i + 1
                else:
                    # Copy the token buffer to the write buffer, and reset the cursor
                    for j in range(0, tag_cursor):
                        write_buffer[write_buffer_cursor] = tag_buffer[j]
                        write_buffer_cursor = write_buffer_cursor + 1
                    tag_cursor = 0
                    current_state = 1

                if tag_cursor == len(TAG_START):
                    tag_cursor = 0
                    current_state = 2

            elif current_state & 8 > 0:
                #print(f"State (8), index {i}")
                # Potential end tag state
                if c == TAG_END[tag_cursor]:
                    tag_buffer[tag_buffer_cursor] = c
                    tag_cursor = tag_cursor + 1
                    i = i + 1
                else:
                    # Copy the token buffer to the write buffer, and reset the cursor
                    for j in range(0, tag_cursor):
                        write_buffer[write_buffer_cursor] = tag_buffer[j]
                        write_buffer_cursor = write_buffer_cursor + 1
                    tag_cursor = 0
                    current_state = 2

                if tag_cursor == len(TAG_END):

                    outfile.write(write_buffer[0:write_buffer_cursor])
                    write_buffer_cursor = 0
                    
                    label = label_buffer[0:label_buffer_cursor].decode("UTF-8")
                    
                    lookup_result = label_func(label, label_func_args)
                    if not lookup_result:
                        outfile.write(f'{{{{{label}}}}}'.encode("UTF-8"))
                    else:
                        outfile.write(lookup_result)

                    tag_cursor = 0
                    label_buffer_cursor = 0
                    
                    current_state = 1
        
        outfile.write(write_buffer[0:write_buffer_cursor])
        write_buffer_cursor = 0

def find_label_in_dic(label, args=None):
    tag_lookup = args
    if label in tag_lookup:
        return tag_lookup[label].encode('utf-8')
    else:
        return None

def stream_and_replace(source_path, dest_path, tag_lookup={}):
    with open(source_path, 'rb') as infile:
        with open(dest_path, 'wb') as outfile:
            replace_text(infile, outfile, find_label_in_dic, tag_lookup)
