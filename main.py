#!/usr/bin/python3

import datetime
import os
import argparse
import pprint
import stat
from pwd import getpwuid
from grp import getgrgid


def ls():
    parser = argparse.ArgumentParser(description="The classic ls command")
    parser.add_argument('directory', type=str, nargs='?', default='.')
    parser.add_argument('-a', '--all', action='store_true', help="Show hidden files")
    parser.add_argument('-l', '--long', action='store_true', help="Show detailed list")
    parser.add_argument('-p', '--permissions', action='store_true', help="Show file permissions")
    parser.add_argument('-hl', '--linked_hard_links', action='store_true', help="Show linked hard links")
    parser.add_argument('-u', '--user', action='store_true', help="Show file user")
    parser.add_argument('-g', '--group', action='store_true', help="Show file group")
    parser.add_argument('-s', '--size', action='store_true', help="Show file size")
    parser.add_argument('-mt', '--modifiedtime', action='store_true', help="Show last modified time")
    args = parser.parse_args()
    allDirs = os.listdir(args.directory)
    if args.all:
        allDirs += [os.curdir, os.pardir]
    else:
        allDirs = [x for x in allDirs if not x[0] == '.']
    allDirs.sort()
    print('total items:', len(allDirs))
    finalResult = []

    if args.long:
        for file in allDirs:
            result = []
            fileStats = os.stat(os.path.join(args.directory, file))
            result.append([getPermissions(fileStats),
                           str(fileStats.st_nlink),
                           str(getpwuid(fileStats.st_uid).pw_name),
                           str(getgrgid(fileStats.st_gid).gr_name),
                           str(fileStats.st_size),
                           prettyTime(fileStats.st_mtime),
                           file
                           ])

            finalResult += result
    else:
        for file in allDirs:
            fileStats = os.stat(os.path.join(args.directory, file))
            result = []
            currentResult = []
            if args.permissions:
                currentResult.append(getPermissions(fileStats))
            if args.linked_hard_links:
                currentResult.append(str(fileStats.st_nlink))
            if args.user:
                currentResult.append(str(getpwuid(fileStats.st_uid).pw_name))
            if args.group:
                currentResult.append(str(getgrgid(fileStats.st_gid).gr_name))
            if args.size:
                currentResult.append(str(fileStats.st_size))
            if args.modifiedtime:
                currentResult.append(prettyTime(fileStats.st_mtime))
            currentResult.append(file)
            result.append(currentResult)
            finalResult += result
    prettyPrint(finalResult)


def getPermissions(fileStats):
    perms = ['r', 'w', 'x']
    if stat.S_ISDIR(fileStats.st_mode):
        currentPerms = ['d']
    elif stat.S_ISLNK(fileStats.st_mode):
        currentPerms = ['l']
    else:
        currentPerms = ['-']
    filePerms = bin(fileStats.st_mode)[-9:]
    for x, perm in enumerate(filePerms):
        if perm == '0':
            currentPerms += '-'
        else:
            currentPerms += perms[x % 3]
    return ''.join(currentPerms)


def prettyPrint(result):
    colWidths = []
    for i in range(0, len(result[0]) - 1):
        col = [col[i] for col in result]
        colWidths.append(len(max(col, key=len)))
    for x in result:
        formattedResult = ' '.join([s.rjust(colWidths[i]) for i, s in enumerate(x[:-1])] + [x[-1]])
        print(formattedResult)


def prettyTime(mtime):
    date = datetime.datetime.fromtimestamp(mtime)
    if date < datetime.datetime.now() - datetime.timedelta(days=365):
        return date.strftime('%b %d  %Y')
    return date.strftime('%b %d %H:%M')


if __name__ == '__main__':
    try:
        ls()
    except OSError as error:
        print(error)
