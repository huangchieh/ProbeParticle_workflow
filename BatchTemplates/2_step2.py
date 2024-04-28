#!/usr/bin/env python3

from ase import Atoms, db
import numpy as np
from ase.io import write

with db.connect("database.db") as fdb:
    for i in range(1, len(fdb) + 1):
        row = fdb.get(i)
        print(row)
        print(row.status)
        if row.status == "done":
            print('Done')
            # save data
            np.save(f"Images/{row.label}.npy", row.data["box"])
            # save system
            write(f"Images/{row.label}.vasp", row.toatoms(), vasp5=True, sort=True)


with db.connect("database.db") as fdb:
    for i in range(1, len(fdb) + 1):
        row = fdb.get(i)
        print(row)
        print(row.status)
        print(row.data["box"] )
        if row.status == "done":
            print('Done')
            # save data
            np.save(f"Images/{row.label}.npy", row.data["box"])
            # save system
            write(f"Images/{row.label}.vasp", row.toatoms(), vasp5=True, sort=True)
