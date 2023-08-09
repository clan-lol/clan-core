"use client"

import * as React from 'react';
import { alpha } from '@mui/material/styles';
import Box from '@mui/material/Box';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TablePagination from '@mui/material/TablePagination';
import TableRow from '@mui/material/TableRow';
import TableSortLabel from '@mui/material/TableSortLabel';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import Checkbox from '@mui/material/Checkbox';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import FormControlLabel from '@mui/material/FormControlLabel';
import Switch from '@mui/material/Switch';
import DeleteIcon from '@mui/icons-material/Delete';
import FilterListIcon from '@mui/icons-material/FilterList';
import { visuallyHidden } from '@mui/utils';
import CircleIcon from '@mui/icons-material/Circle';
import Stack from '@mui/material/Stack/Stack';
import ModeIcon from '@mui/icons-material/Mode';
import ClearIcon from '@mui/icons-material/Clear';
import Fade from '@mui/material/Fade/Fade';

interface Data {
  name: string;
  id: string;
  status: boolean;
  last_seen: number;
}

function createData(
  name: string,
  id: string,
  status: boolean,
  last_seen: number,

): Data {
  if (status && last_seen > 0) {
    console.error("Last seen should be 0 if status is true");
  }

  return {
    name,
    id,
    status,
    last_seen: last_seen,
  };
}

const rows = [
  createData('Matchbox', "42:0:f21:6916:e333:c47e:4b5c:e74c", true, 0),
  createData('Ahorn', "42:0:3c46:b51c:b34d:b7e1:3b02:8d24", true, 0),
  createData('Yellow', "42:0:3c46:98ac:9c80:4f25:50e3:1d8f", false, 16.0),
  createData('Rauter', "42:0:61ea:b777:61ea:803:f885:3523", false, 6.0),
  createData('Porree', "42:0:e644:4499:d034:895e:34c8:6f9a", false, 13),
  createData('Helsinki', "42:0:3c46:fd4a:acf9:e971:6036:8047", true, 0),
  createData('Kelle', "42:0:3c46:362d:a9aa:4996:c78e:839a", true, 0),
  createData('Shodan', "42:0:3c46:6745:adf4:a844:26c4:bf91", true, 0.0),
  createData('Qubasa', "42:0:3c46:123e:bbea:3529:db39:6764", false, 7.0),
  createData('Green', "42:0:a46e:5af:632c:d2fe:a71d:cde0", false, 2),
  createData('Gum', "42:0:e644:238d:3e46:c884:6ec5:16c", false, 0),
  createData('Xu', "42:0:ca48:c2c2:19fb:a0e9:95b9:794f", true, 0),
  createData('Zaatar', "42:0:3c46:156e:10b6:3bd6:6e82:b2cd", true, 0),
];

function descendingComparator<T>(a: T, b: T, orderBy: keyof T) {
  if (b[orderBy] < a[orderBy]) {
    return -1;
  }
  if (b[orderBy] > a[orderBy]) {
    return 1;
  }
  return 0;
}

type Order = 'asc' | 'desc';

function getComparator<Key extends keyof any>(
  order: Order,
  orderBy: Key,
): (
  a: { [key in Key]: number | string | boolean },
  b: { [key in Key]: number | string | boolean },
) => number {
  return order === 'desc'
    ? (a, b) => descendingComparator(a, b, orderBy)
    : (a, b) => -descendingComparator(a, b, orderBy);
}

// Since 2020 all major browsers ensure sort stability with Array.prototype.sort().
// stableSort() brings sort stability to non-modern browsers (notably IE11). If you
// only support modern browsers you can replace stableSort(exampleArray, exampleComparator)
// with exampleArray.slice().sort(exampleComparator)
function stableSort<T>(array: readonly T[], comparator: (a: T, b: T) => number) {
  const stabilizedThis = array.map((el, index) => [el, index] as [T, number]);
  stabilizedThis.sort((a, b) => {
    const order = comparator(a[0], b[0]);
    if (order !== 0) {
      return order;
    }
    return a[1] - b[1];
  });
  return stabilizedThis.map((el) => el[0]);
}

interface HeadCell {
  disablePadding: boolean;
  id: keyof Data;
  label: string;
  alignRight: boolean;
}

const headCells: readonly HeadCell[] = [
  {
    id: 'name',
    alignRight: false,
    disablePadding: false,
    label: 'Display Name & ID',
  },
  {
    id: 'status',
    alignRight: false,
    disablePadding: false,
    label: 'Status',
  },
  {
    id: 'last_seen',
    alignRight: false,
    disablePadding: false,
    label: 'Last Seen',
  },
];

interface EnhancedTableProps {
  onRequestSort: (event: React.MouseEvent<unknown>, property: keyof Data) => void;
  order: Order;
  orderBy: string;
  rowCount: number;
}

function EnhancedTableHead(props: EnhancedTableProps) {
  const { order, orderBy, onRequestSort } =
    props;
  const createSortHandler =
    (property: keyof Data) => (event: React.MouseEvent<unknown>) => {
      onRequestSort(event, property);
    };

  return (
    <TableHead>
      <TableRow>
        {headCells.map((headCell) => (
          <TableCell
            key={headCell.id}
            align={headCell.alignRight ? 'right' : 'left'}
            padding={headCell.disablePadding ? 'none' : 'normal'}
            sortDirection={orderBy === headCell.id ? order : false}
          >
            <TableSortLabel
              active={orderBy === headCell.id}
              direction={orderBy === headCell.id ? order : 'asc'}
              onClick={createSortHandler(headCell.id)}
            >
              {headCell.label}
              {orderBy === headCell.id ? (
                <Box component="span" sx={visuallyHidden}>
                  {order === 'desc' ? 'sorted descending' : 'sorted ascending'}
                </Box>
              ) : null}
            </TableSortLabel>
          </TableCell>
        ))}
      </TableRow>
    </TableHead>
  );
}

interface EnhancedTableToolbarProps {
  selected: string | undefined;
  onClear: () => void;
}

function renderLastSeen(last_seen: number) {
  return (
    <Typography component="div" align="left" variant="body1">
      {last_seen} days ago
    </Typography>
  );
}

function renderName(name: string, id: string) {
  return (
    <Stack>
      <Typography component="div" align="left" variant="body1">
        {name}
      </Typography>
      <Typography color="grey" component="div" align="left" variant="body2">
        {id}
      </Typography>
    </Stack>
  );
}

function renderStatus(status: boolean) {
  if (status) {
    return (
      <Stack direction="row" alignItems="center" gap={1}>
        <CircleIcon color="success" style={{ fontSize: 15 }} />
        <Typography component="div" align="left" variant="body1">
          Online
        </Typography>
      </Stack>
    );
  }
  return (
    <Stack direction="row" alignItems="center" gap={1}>
      <CircleIcon color="error" style={{ fontSize: 15 }} />
      <Typography component="div" align="left" variant="body1">
        Offline
      </Typography>
    </Stack>
  );
}

function EnhancedTableToolbar(props: EnhancedTableToolbarProps) {
  const { selected, onClear } = props;
  const somethingSelected = selected !== undefined;

  const handleSomethingSelected = () => {

    if (somethingSelected) {
      return (

        <Toolbar
          sx={{
            pl: { sm: 2 },
            pr: { xs: 1, sm: 1 },
            bgcolor: (theme) =>
              alpha(theme.palette.primary.main, theme.palette.action.activatedOpacity),
          }}>
          <Tooltip title="Clear">
            <IconButton onClick={onClear}>
              <ClearIcon />
            </IconButton>
          </Tooltip>
          <Typography
            sx={{ flex: '1 1 100%' }}
            color="inherit"
            style={{ fontSize: 18, marginBottom: 2.5, marginLeft: 3 }}
            component="div"
          >
            {selected} selected
          </Typography>
          <Tooltip title="Edit">
            <IconButton>
              <ModeIcon />
            </IconButton>
          </Tooltip>
        </Toolbar >


      );
    } else {
      return (

        <Toolbar
          sx={{
            pl: { sm: 2 },
            pr: { xs: 1, sm: 1 }
          }}>
          <Typography
            sx={{ flex: '1 1 100%' }}
            variant="h6"
            id="tableTitle"
            component="div"
          >
            Nodes
          </Typography>
          <Tooltip title="Filter list">
            <IconButton>
              <FilterListIcon />
            </IconButton>
          </Tooltip>
        </Toolbar >

      );
    }
  };

  return handleSomethingSelected();
}

export default function EnhancedTable() {
  const [order, setOrder] = React.useState<Order>('asc');
  const [orderBy, setOrderBy] = React.useState<keyof Data>('status');
  const [selected, setSelected] = React.useState<string | undefined>(undefined);
  const [page, setPage] = React.useState(0);
  const [dense, setDense] = React.useState(false);
  const [rowsPerPage, setRowsPerPage] = React.useState(5);

  const handleRequestSort = (
    event: React.MouseEvent<unknown>,
    property: keyof Data,
  ) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const handleClick = (event: React.MouseEvent<unknown>, name: string) => {
    if (selected === name) {
      setSelected(undefined);
    } else {
      setSelected(name);
    }
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleChangeDense = (event: React.ChangeEvent<HTMLInputElement>) => {
    setDense(event.target.checked);
  };

  // TODO: Make a number to increase comparison speed and ui performance
  const isSelected = (name: string) => name === selected;

  // Avoid a layout jump when reaching the last page with empty rows.
  const emptyRows =
    page > 0 ? Math.max(0, (1 + page) * rowsPerPage - rows.length) : 0;

  const visibleRows = React.useMemo(
    () =>
      stableSort(rows, getComparator(order, orderBy)).slice(
        page * rowsPerPage,
        page * rowsPerPage + rowsPerPage,
      ),
    [order, orderBy, page, rowsPerPage],
  );

  return (
    <Box sx={{ width: '100%' }}>
      <Paper sx={{ width: '100%', mb: 2 }} id="test">
        <EnhancedTableToolbar selected={selected} onClear={() => setSelected(undefined)} />
        <TableContainer>
          <Table
            sx={{ minWidth: 750 }}
            aria-labelledby="tableTitle"
            size={dense ? 'small' : 'medium'}
          >
            <EnhancedTableHead
              order={order}
              orderBy={orderBy}
              onRequestSort={handleRequestSort}
              rowCount={rows.length}
            />
            <TableBody>
              {visibleRows.map((row, index) => {
                const isItemSelected = isSelected(row.name);
                const labelId = `enhanced-table-checkbox-${index}`;

                return (
                  <TableRow
                    hover
                    onClick={(event) => handleClick(event, row.name)}
                    role="checkbox"
                    aria-checked={isItemSelected}
                    tabIndex={-1}
                    key={row.name}
                    selected={isItemSelected}
                    sx={{ cursor: 'pointer' }}
                  >
                    {/* <TableCell padding="checkbox">
                      <Checkbox
                        color="primary"
                        checked={isItemSelected}
                        inputProps={{
                          'aria-labelledby': labelId,
                        }}
                      />
                    </TableCell> */}
                    <TableCell
                      component="th"
                      id={labelId}
                      scope="row"
                    >
                      {renderName(row.name, row.id)}
                    </TableCell>
                    <TableCell align="right">{renderStatus(row.status)}</TableCell>
                    <TableCell align="right">{renderLastSeen(row.last_seen)}</TableCell>
                  </TableRow>
                );
              })}
              {emptyRows > 0 && (
                <TableRow
                  style={{
                    height: (dense ? 33 : 53) * emptyRows,
                  }}
                >
                  <TableCell colSpan={6} />
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        {/* TODO: This creates the error Warning: Prop `id` did not match. Server: ":RspmmcqH1:" Client: ":R3j6qpj9H1:" */}
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={rows.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>
      <FormControlLabel
        control={<Switch checked={dense} onChange={handleChangeDense} />}
        label="Dense padding"
      />
    </Box>
  );
}
