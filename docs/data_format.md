# Input data format

Each regional input directory contains three UTF-8 CSV files.

## `events.csv`

| Column | Meaning |
|---|---|
| `event_id` | Contiguous zero-based event index in chronological order |
| `time` | Catalog time in a documented, internally consistent unit |
| `magnitude` | Event magnitude used for source selection |
| `cell_id` | Assigned fault-associated cell; use `-1` if unassigned |

## `event_pairs.csv`

| Column | Meaning |
|---|---|
| `source` | Earlier event index |
| `target` | Later event index |
| `probability` | ETAS-inferred event-pair triggering probability |

## `cells.csv`

| Column | Meaning |
|---|---|
| `cell_id` | Contiguous zero-based cell index |
| `longitude` | Cell-center longitude in decimal degrees |
| `latitude` | Cell-center latitude in decimal degrees |

The repository treats ETAS probabilities as prepared scientific inputs. The
paper-specific catalog preparation and ETAS fitting metadata should accompany
the archived data record, because redistribution rights differ among catalog
and fault-data providers.
