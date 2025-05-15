import tarfile
from pathlib import Path
from tempfile import TemporaryDirectory

from clan_lib.errors import ClanError

from clan_cli.cmd import Log, RunOpts
from clan_cli.ssh.host import Host


def upload(
    host: Host,
    local_src: Path,
    remote_dest: Path,  # must be a directory
    file_user: str = "root",
    file_group: str = "root",
    dir_mode: int = 0o700,
    file_mode: int = 0o400,
) -> None:
    # Check the depth of the remote destination path to prevent accidental deletion
    # of important directories like /home/user when uploading a directory,
    # as the process involves `rm -rf` on the destination.
    if local_src.is_dir():
        # Calculate the depth (number of components after the root '/')
        # / -> depth 0
        # /a -> depth 1
        # /a/b -> depth 2
        # /a/b/c -> depth 3
        depth = len(remote_dest.parts) - 1

        # General rule: destination must be at least 3 levels deep for safety.
        is_too_shallow = depth < 3

        # Exceptions: Allow depth 2 if the path starts with /tmp/, /root/, or /etc/.
        # This allows destinations like /tmp/mydir or /etc/conf.d, but not /tmp or /etc directly.
        is_allowed_exception = depth >= 2 and (
            str(remote_dest).startswith("/tmp/")
            or str(remote_dest).startswith("/root/")
            or str(remote_dest).startswith("/etc/")
        )

        # Raise error if the path is too shallow and not an allowed exception.
        if is_too_shallow and not is_allowed_exception:
            msg = (
                f"When uploading a directory, the remote destination '{remote_dest}' is considered unsafe "
                f"(depth {depth}). It must be at least 3 levels deep (e.g., /path/to/dir), "
                f"or at least 2 levels deep starting with /tmp/, /root/, or /etc/ (e.g., /tmp/mydir). "
                f"Reason: The existing destination '{remote_dest}' will be recursively deleted ('rm -rf') before upload."
            )
            raise ClanError(msg)

    # Create the tarball from the temporary directory
    with TemporaryDirectory(prefix="facts-upload-") as tardir:
        tar_path = Path(tardir) / "upload.tar.gz"
        # We set the permissions of the files and directories in the tarball to read only and owned by root
        # As first uploading the tarball and then changing the permissions can lead an attacker to
        # do a race condition attack
        with tarfile.open(str(tar_path), "w:gz") as tar:
            if local_src.is_dir():
                # Handle directory upload
                for root, dirs, files in local_src.walk():
                    for mdir in dirs:
                        dir_path = Path(root) / mdir
                        tarinfo = tar.gettarinfo(
                            dir_path,
                            arcname=str(dir_path.relative_to(str(local_src))),
                        )
                        tarinfo.mode = dir_mode
                        tarinfo.uname = file_user
                        tarinfo.gname = file_group
                        tar.addfile(tarinfo)
                    for file in files:
                        file_path = Path(root) / file
                        tarinfo = tar.gettarinfo(
                            file_path,
                            arcname=str(file_path.relative_to(str(local_src))),
                        )
                        tarinfo.mode = file_mode
                        tarinfo.uname = file_user
                        tarinfo.gname = file_group
                        with file_path.open("rb") as f:
                            tar.addfile(tarinfo, f)
            else:
                # Handle single file upload
                tarinfo = tar.gettarinfo(local_src, arcname=remote_dest.name)
                tarinfo.mode = file_mode
                tarinfo.uname = file_user
                tarinfo.gname = file_group
                with local_src.open("rb") as f:
                    tar.addfile(tarinfo, f)

        cmd = None
        if local_src.is_dir():
            cmd = 'install -d -m "$1" "$0" && find "$0" -mindepth 1 -delete && tar -C "$0" -xzf -'
        elif local_src.is_file():
            cmd = 'rm -f "$0" && tar -C "$(dirname "$0")" -xzf -'
        else:
            msg = f"Unsupported source type: {local_src}"
            raise ClanError(msg)

        # TODO accept `input` to be  an IO object instead of bytes so that we don't have to read the tarfile into memory.
        with tar_path.open("rb") as f:
            host.run(
                [
                    "bash",
                    "-c",
                    cmd,
                    str(remote_dest),
                    f"{dir_mode:o}",
                ],
                RunOpts(
                    input=f.read(),
                    log=Log.BOTH,
                    prefix=host.command_prefix,
                    needs_user_terminal=True,
                ),
                become_root=True,
            )
