"use client";

import { Machine } from "@/api/model/machine";
import SearchIcon from "@mui/icons-material/Search";
import { Autocomplete, InputAdornment, TextField } from "@mui/material";
import IconButton from "@mui/material/IconButton";
import { Dispatch, SetStateAction, useEffect, useMemo, useState } from "react";
import { useDebounce } from "../hooks/useDebounce";
import { MachineFilter } from "../hooks/useMachines";

export interface SearchBarProps {
  allData: Machine[];
  setQuery: Dispatch<SetStateAction<MachineFilter>>;
}

export function SearchBar(props: SearchBarProps) {
  const { allData, setQuery } = props;
  const [search, setSearch] = useState<string>("");
  const debouncedSearch = useDebounce(search, 250);
  const [open, setOpen] = useState(false);

  // Define a function to handle the Esc key press
  function handleEsc(event: React.KeyboardEvent<HTMLDivElement>) {
    if (event.key === "Escape") {
      setSearch("");
    }

    // check if the key is Enter
    if (event.key === "Enter") {
      setOpen(false);
    }
  }

  useEffect(() => {
    setQuery((filters) => ({ ...filters, name: debouncedSearch }));
  }, [debouncedSearch, setQuery]);

  const handleInputChange = (event: any, value: string) => {
    console.log({ value });
    setSearch(value);
  };

  const options = useMemo(() => allData.map((row) => row.name), [allData]);

  return (
    <Autocomplete
      freeSolo
      autoComplete
      options={options}
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
