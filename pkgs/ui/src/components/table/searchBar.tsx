"use client";

import {
  SetStateAction,
  Dispatch,
  useState,
  useEffect,
  useRef,
  useMemo,
  ClassAttributes,
  JSX,
  Key,
  LiHTMLAttributes,
} from "react";
import IconButton from "@mui/material/IconButton";
import Tooltip from "@mui/material/Tooltip";
import SearchIcon from "@mui/icons-material/Search";
import { useDebounce } from "../hooks/useDebounce";
import { TableData } from "@/data/nodeData";
import {
  Autocomplete,
  Box,
  Container,
  InputAdornment,
  Stack,
  TextField,
} from "@mui/material";

export interface SearchBarProps {
  tableData: TableData[];
  setFilteredList: Dispatch<SetStateAction<TableData[]>>;
}

export function SearchBar(props: SearchBarProps) {
  let { tableData, setFilteredList } = props;
  const [search, setSearch] = useState<string>("");
  const debouncedSearch = useDebounce(search, 250);
  const [open, setOpen] = useState(true);

  // Define a function to handle the Esc key press
  function handleEsc(event: React.KeyboardEvent<HTMLDivElement>) {
    if (event.key === "Escape") {
      setSearch("");
      setFilteredList(tableData);
    }

    // check if the key is Enter
    if (event.key === "Enter") {
      setOpen(false);
    }
  }

  useEffect(() => {
    if (debouncedSearch) {
      const filtered: TableData[] = tableData.filter((row) => {
        return row.name.toLowerCase().includes(debouncedSearch.toLowerCase());
      });
      setFilteredList(filtered);
    }
  }, [debouncedSearch, tableData, setFilteredList]);

  const handleInputChange = (event: any, value: string) => {
    if (value === "") {
      setFilteredList(tableData);
    }

    setSearch(value);
  };

  const suggestions = useMemo(
    () => tableData.map((row) => row.name),
    [tableData],
  );

  return (
    <Autocomplete
      freeSolo
      autoComplete
      options={suggestions}
      renderOption={(props: any, option: any) => {
        return (
          <li {...props} key={option}>
            {option}
          </li>
        );
      }}
      onKeyDown={handleEsc}
      onInputChange={handleInputChange}
      value={search}
      open={open}
      onOpen={() => {
        setOpen(true);
      }}
      onClose={() => {
        setOpen(false);
      }}
      renderInput={(params) => (
        <TextField
          {...params}
          fullWidth
          label="Search"
          variant="outlined"
          autoComplete="nickname"
          InputProps={{
            ...params.InputProps,
            startAdornment: (
              <InputAdornment position="start">
                <IconButton>
                  <SearchIcon />
                </IconButton>
              </InputAdornment>
            ),
          }}
        ></TextField>
      )}
    />
  );
}
