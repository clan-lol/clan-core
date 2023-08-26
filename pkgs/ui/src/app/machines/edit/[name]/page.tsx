interface DeviceEditProps {
  params: { name: string };
}

export default function EditDevice(props: DeviceEditProps) {
  const {
    params: { name },
  } = props;
  return <div>{name}</div>;
}
