"use client";

import {
  SetStateAction,
  Dispatch,
  useState,
  useEffect,
  useRef,
  useMemo,
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

  // Define a function to handle the Esc key press
  function handleEsc(event: React.KeyboardEvent<HTMLDivElement>) {
    if (event.key === "Escape") {
      console.log("Escape key pressed");
      setSearch("");
      setFilteredList(tableData);
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

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.value === "") {
      setFilteredList(tableData);
    }
    setSearch(e.target.value);
  };

  const suggestions = useMemo(
    () => tableData.map((row) => row.name),
    [tableData],
  );

  return (
    <Autocomplete
      freeSolo
      options={suggestions}
      onKeyDown={handleEsc}
      onChange={(event, value) => {
        // do something with the selected value
        if (value === null) {
          setSearch("");
          setFilteredList(tableData);
        } else {
          setSearch(value);
        }
      }}
      renderInput={(params) => (
        <TextField
          {...params}
          fullWidth
          label="Search"
          variant="outlined"
          value={search}
          onChange={handleInputChange}
          autoComplete="nickname"
          InputProps={{
            ...params.InputProps,
            // endAdornment: (
            //   <InputAdornment position="end">
            //     <IconButton>
            //       <SearchIcon />
            //     </IconButton>
            //   </InputAdornment>
            // ),
          }}
        >
          {/* {suggestions.map((item, index) => (
                <option key={index} onClick={() => handleSelect(item)}>
                  {item}
                </option>
              ))} */}
        </TextField>
      )}
    />
  );
}
