def treeview_sort_column(tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    if col == "Stock":
        l.sort(key=lambda x: int(x[0]), reverse=reverse)
    else:
        l.sort(reverse=reverse)

    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)

    for column in tv["columns"]:
        tv.heading(column, text=column)
    if reverse:
        tv.heading(col, text=f"{col} ▲")
    else:
        tv.heading(col, text=f"{col} ▼")

    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))
