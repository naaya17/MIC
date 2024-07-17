# MIC - Memory analysis of IndexedDB data on Chromium-based applications

## Usage

```bash
usage: main.py [-h] [-d] [-q] [--log_file _LOG_FILE] memory_dump_file
```

## Description

This is a codebase project designed to parse and interpret structures related to IndexedDB from memory dumps containing Chromium-based service usage. It utilizes the `deserializer` module from the [ccl_solution_group](https://github.com/cclgroupltd/ccl_chrome_indexeddb) library to deserialize values, specifically for `blink_value` and `v8_value`.

## Positional Arguments

- `memory_dump_file`: Path to the memory dump file in the Windows Minidump file format.

## Options

- `-h`, `--help`: Show this help message and exit.
- `-d`, `--debug`: Enable debug output.
- `-q`, `--quiet`: Disable informational output.
- `--log_file _LOG_FILE`: Path to the log file.

## Example Usage

```bash
python main.py memory.dmp 
```
## Dataset

The dataset contains personal information, so only datset of `Experiment #1` and `Experiment #2` are uploaded. You can download them from the links below:

- [Experiment #1](https://www.dropbox.com/scl/fi/2v63607njm82j263ervab/Chrome-Normal-Records.dmp?rlkey=u94qxo5763yj5tvmhtg96okkc&st=3mgnk4at&dl=0) 
- [Experiment #2](https://www.dropbox.com/scl/fi/3waij5oe5yb7yb5ggo805/Chrome-Modified-Records.dmp?rlkey=oetqv9tkscu8tc4lrsvthl0d3&st=5wwlt0ad&dl=0)

## This project was submitted to `DFRWS APAC 2024` and will be made publicly available in the future.