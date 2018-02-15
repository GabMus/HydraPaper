def empty_listbox(listbox):
    while True:
        row = listbox.get_row_at_index(0)
        if row:
            listbox.remove(row)
        else:
            break
