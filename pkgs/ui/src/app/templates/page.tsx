import { ChevronRight } from "@mui/icons-material";
import {
  Avatar,
  Divider,
  List,
  ListItem,
  ListItemAvatar,
  ListItemButton,
  ListItemSecondaryAction,
  ListItemText,
  Typography,
} from "@mui/material";

const templates = [
  {
    id: "1",
    name: "Office Preset",
    date: "12 May 2050",
  },
  {
    id: "2",
    name: "Work",
    date: "30 Feb 2020",
  },
  {
    id: "3",
    name: "Family",
    date: "1 Okt 2022",
  },
  {
    id: "4",
    name: "Standard",
    date: "24 Jul 2021",
  },
];

export default function ImageOverview() {
  return (
    <div className="flex flex-col items-center justify-center">
      <Typography variant="h4">Templates</Typography>
      <List className="w-full gap-y-4">
        {templates.map(({ id, name, date }, idx, all) => (
          <>
            <ListItem key={id}>
              <ListItemButton LinkComponent={"a"} href={`/templates/${id}`}>
                <ListItemAvatar>
                  <Avatar className="bg-purple-40">{name.slice(0, 1)}</Avatar>
                </ListItemAvatar>
                <ListItemText primary={name} secondary={date} />
                <ListItemSecondaryAction>
                  <ChevronRight />
                </ListItemSecondaryAction>
              </ListItemButton>
            </ListItem>
            {idx < all.length - 1 && <Divider flexItem className="mx-10" />}
          </>
        ))}
      </List>
    </div>
  );
}
