import csv
from os.path import join, abspath
import os
from api.database import engine, session
from api.models import SourceDest
from sqlalchemy.exc import IntegrityError

data_dir = abspath(join('data', 'raw_data', 'transitskims100'))

time_fields = {
    'mf22.txt': 'in_vehicle_time', 
    'mf23.txt': 'walk_transfer_time', 
    'mf24.txt': 'wait_time',
}

if __name__ == "__main__":
    for source_file in ['mf22.txt', 'mf23.txt', 'mf24.txt']:
        fpath = join(data_dir, source_file)
        time_col = time_fields[source_file]
        fields = [
            'source', 
            'dest', 
            time_col,
        ]
        table = SourceDest.__table__
        conn = engine.connect()
        with open(fpath, 'rU') as f:
            [f.next() for i in range(4)]
            for line in f:
                parts = line.strip().split(' ')
                source = parts[0]
                destinations = [i.split(':') for i in parts[1:]]
                vals = []
                for dest in destinations:
                    vals.append({k:v for k,v in zip(fields,(source, dest[0], dest[1],))})
                ins = table.insert()
                try:
                    conn.execute(ins, vals)
                except IntegrityError:
                    for val in vals:
                        u = {time_col: val[time_col]}
                        upd = table.update().where(table.c.source == val['source'])\
                            .where(table.c.dest == val['dest'])\
                            .values(**u)
                        conn.execute(upd)