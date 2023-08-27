"use client";

import { ChangeEvent, SetStateAction, Dispatch } from "react";
import IconButton from "@mui/material/IconButton";
import Tooltip from "@mui/material/Tooltip";
import SearchIcon from "@mui/icons-material/Search";

export interface SearchBarProps {
  search: string;
  setSearch: Dispatch<SetStateAction<string>>;
}

export function SearchBar(props: SearchBarProps) {
  const { search, setSearch } = props;
  const handleSearch = (event: ChangeEvent<HTMLInputElement>) => {
    setSearch(event.target.value);
  };

  return (
    <label htmlFor="search">
      <Tooltip title="Filter list">
        <IconButton>
          <SearchIcon />
        </IconButton>
      </Tooltip>
      <input id="search" type="text" value={search} onChange={handleSearch} />
    </label>
  );
}
