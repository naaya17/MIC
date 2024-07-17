#!/usr/bin/env python3
import os
import textwrap
import datetime
import argparse
import loggers
import logger
import tqdm

from minidump.minidumpfile import MinidumpFile
from minidump.streams import MemoryType, MemoryState, AllocationProtect
from classes.DBImpl import DBImpl

NAME = 'MIC'
VERSION = '1.0'
DESCRIPTION = textwrap.dedent('\n'.join([
        '',
        'MIC',
        '']))
EPILOG = textwrap.dedent('\n'.join([
        '',
        'Example usage:',
        '',
        '\"python main.py memory.dmp [Windows Minidump file format]\"',
        '']))

def AddLoggerOptions(argument_group):
    argument_group.add_argument(
        '-d', '--debug', dest='debug', action='store_true', default=False,
        help='Enable debug output.')

    argument_group.add_argument(
        '-q', '--quiet', dest='quiet', action='store_true', default=False,
        help='Disable informational output.')
    
    argument_group.add_argument(
        '--log_file', dest='_log_file', type=str, default=False, 
        help='path to log file.')

def main():
    argument_parser = argparse.ArgumentParser(
            description=DESCRIPTION, epilog=EPILOG,
            formatter_class=argparse.RawDescriptionHelpFormatter)
    
    argument_parser.add_argument('memory_dump_file', type=str, help='path to memory dump [Windows Minidump file format] file.')
    
    logger_group = argument_parser.add_argument_group('loggers')
    AddLoggerOptions(logger_group)

    args = argument_parser.parse_args()
    _log_file = args._log_file
    _debug_mode = getattr(args, 'debug', False)
    _quiet_mode = getattr(args, 'quiet', False)

    if not _log_file:
        os.mkdir('results')
        local_date_time = datetime.datetime.now()
        _log_file = (
                'results/{0:s}-{1:04d}{2:02d}{3:02d}T{4:02d}{5:02d}{6:02d}.log.gz').format(
                NAME, local_date_time.year, local_date_time.month,
                local_date_time.day, local_date_time.hour, local_date_time.minute,
                local_date_time.second)
        _out_file = (
                'results/{0:s}-{1:04d}{2:02d}{3:02d}T{4:02d}{5:02d}{6:02d}.output.json').format(
                os.path.split(args.memory_dump_file)[1], local_date_time.year, local_date_time.month,
                local_date_time.day, local_date_time.hour, local_date_time.minute,
                local_date_time.second)
    
    loggers.ConfigureLogging(
            debug_output=_debug_mode, filename=_log_file,
            quiet_mode=_quiet_mode)
    
    
    if not os.path.exists(args.memory_dump_file):
        print(f'No such file: {args.memory_dump_file}')
        exit()

    minidmp = MinidumpFile.parse(args.memory_dump_file)
    logger.info(f'Input File: '.format(args.memory_dump_file))
    num = 0
    total = 0
    vads = []
    for vad in minidmp.memory_info.infos:
        if vad.Protect == AllocationProtect.PAGE_READWRITE and vad.State == MemoryState.MEM_COMMIT and vad.Type == MemoryType.MEM_PRIVATE:
            vads.append(vad)
            total += vad.RegionSize

    with open(_out_file, 'a', encoding='utf-8') as f:
        f.write(f'{{')
    for vad in tqdm.tqdm(vads, position=0):
        chunk = minidmp.get_reader().read(vad.BaseAddress, vad.RegionSize)
        for offset in tqdm.tqdm(range(0, vad.RegionSize - 0x278, 8), position=1, leave=False):
            buff = chunk[offset:offset + 0x278]
            ret = _work(minidmp, buff, offset+vad.BaseAddress)
            if ret is not None:
                with open(_out_file, 'a', encoding='utf-8') as f:
                    num += 1
                    f.write(f'"DBImpl{num}":\n')
                    f.write(str(ret) + "\n,")
        
    with open(_out_file, 'a', encoding='utf-8') as f:
        f.write(f'}}')

def _work(minidmp, buff, base_addr):
    try:
        root = DBImpl(minidmp, buff, base_addr)
        if root.validate():
            root.set_values()
            return root
    except Exception as exception:
        pass

if __name__ == '__main__':
    main()
