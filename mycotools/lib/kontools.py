#! /usr/bin/env python3

import datetime, sys, glob, os, re, subprocess, numpy as np

def eprint( *args, **kwargs ):
    '''Prints to stderr'''

    print(*args, file = sys.stderr, **kwargs )


def vprint( toPrint, v = False ):
    '''Boolean print option'''

    if v:
        print( toPrint, flush = True )


def gunzip( gzip_file, remove = True ):
    '''gunzips gzip_file and removes if successful'''

    new_file = re.sub( r'\.gz$', '', gzip_file )
    #try:
    with gzip.open(gzip_file, 'rb') as f_in:
        with open(new_file, 'w') as f_out:
            shutil.copyfileobj(f_in, f_out)
    if remove:
        os.remove( gzip_file )
    return new_file
#    except:
 #       if os.path.isfile( new_file ):
  #          if os.path.isfile( gzip_file ):
   #             os.remove( new_file )
    return False


def expandEnvVar( path ):
    '''Expands environment variables by regex substitution'''

    if path.startswith( '/$' ):
        path = '/' + path
    env_comp = re.compile( r'/\$([^/]+)' )
    if not env_comp.search( path ):
        env_comp = re.compile( r'^\$([^/]+)' )
    var_search = env_comp.search( path )
    if var_search:
        var = var_search[1]
        pathChange = os.environ[ var ]
        path = env_comp.sub( pathChange, path )

    return path


def formatPath( path, isdir = None ):
    '''Goal is to convert all path types to absolute path with explicit dirs'''
   
    if path:
        path = os.path.expanduser( path )
        path = expandEnvVar( path )
        path = os.path.abspath( path )
        if isdir:
            if not path.endswith('/'):
                path += '/'
        else:
            if path.endswith( '/' ):
                if path.endswith( '//' ):
                    path = path[:-1]
                if not os.path.isdir( path ):
                    path = path[:-1]
            elif not path.endswith( '/' ):
                if os.path.isdir( path ):
                    path += '/'

    return path


# need to change recursive to false
def collect_files( directory = './', filetype = '*', recursive = False ):
    '''
    Inputs: directory path, file extension (no "."), recursivity bool
    Outputs: list of files with `filetype`
    If the filetype is a list, split it, else make a list of the one entry.
    Parse the environment variable if applicable. Then, obtain a clean, full 
    version of the input directory. Glob to obtain the filelist for each 
    filetype based on whether or not it is recursive.
    '''

    if type(filetype) == list:
        filetypes = filetype.split()
    else:
        filetypes = [filetype]

    directory = formatPath( directory )
    filelist = []
    for filetype in filetypes:
        if recursive:
            filelist.extend( 
                glob.glob( directory + "/**/*." + filetype, recursive = recursive )
            )
        else:
            filelist.extend(
                glob.glob( directory + "/*." + filetype, recursive = recursive ) 
            )

    return filelist


def collect_folders( directory, recursive = False ):
    '''
    Inputs: directory path, recursive search boolean
    Outputs: list of folders
    Get folders via os, recursively extend output list if True.
    '''

    directory = formatPath( directory )
    folders_prep = os.listdir( directory )
    folders = [ 
        directory + '/' + folder + '/' for folder in folders_prep \
        if os.path.isdir( directory + '/' + folder ) 
    ]

    if recursive:
        for folder in folders:
            folders.extend(collect_folders( folder, recursive ))

    return folders


def dictSplit( Dict, factor ):
    '''
    Inputs: a dictionary `Dict`, and an integer `factor` to split by
    Outputs: a list of split dictionaries `list_dict`
    Split dictionary keys into a numpy array via the factor. For each
    key, append a new dictionary to the output list and populate it 
    with the list of keys within that factor. The last entry will be
    whatever amount is leftover.
    '''
    

    list_dict = []
    keys_list = np.array_split( list(Dict.keys()), factor )
    
    for keys in keys_list:
        list_dict.append( {} )
        for key in keys:
            list_dict[-1][key] = Dict[key]

    return list_dict
    

def sysStart( args, usage, min_len, dirs = [], files = [] ):

    if '-h' in args or '--help' in args:
        print( '\n' + usage + '\n' )
        sys.exit( 1 )
    elif len( args ) < min_len:
        print( '\n' + usage + '\n' )
        sys.exit( 2 )
    elif not all( os.path.isfile( x ) for x in files ):
        print( '\n' + usage )
        eprint( 'ERROR: input file(s) do not exist\n' )
        sys.exit( 3 )
    elif not all( os.path.isfile( x ) for x in dirs ):
        print( '\n' + usage )
        eprint( 'ERROR: input directory does not exist\n' )
        sys.exit( 4 )

    return args

 
def intro( script_name, args_dict, credit='', log = False, stdout = True):
    '''
    Inputs: script_name string, args_dict dictionary of arguments, 
    credit string bool / path for output log
    Outputs: prints an introduction, returns start_time in YYYYmmdd format
    Creates a string to populate and format for the introduction using 
    keys as the left-most descriptor and arguments (values) as the right
    most. Optionally outputs a log according to `log` path.
    '''

    start_time = datetime.datetime.now()
    date = start_time.strftime( '%Y%m%d' )

    out_str = '\n' + script_name + '\n' + credit + \
        '\nExecution began: ' + str(start_time)

    for arg in args_dict:
        out_str += '\n' + '{:<30}'.format(arg.upper() + ':') + \
            str(args_dict[ arg ])

    if stdout:
        print( out_str, flush = True )
    if log:
        out_file = os.path.abspath( log ) + '/' + date + '.log'
        count = 0
        while os.path.exists( out_file ):
            count += 1
            out_file = os.path.abspath( log ) + '/' + date + '_' + \
                str(count) + '.log'

        with open(out_file, 'w') as out:
            out.write( out_str )

    return start_time


def outro( start_time, log = False, stdout = True ):
    '''
    Inputs: start time string formatted YYYYmmdd, log path
    Outputs: prints execution time and exits with 0 status
    '''

    if stdout:
        end_time = datetime.datetime.now()
        duration = end_time - start_time
        dur_min = duration.seconds/60
        print('\nExecution finished:', str(end_time) + '\t' + \
            '\n\t{:.2}'.format(dur_min), 'minutes\n')
    sys.exit(0)


def prep_output(output, mkdir = True, require_newdir = False, cd = False):
    '''
    Inputs: output path, bool `mkdir`, bool `require_newdir`, bool cd.
    Outputs: creates directory, returns None if bool inputs fail, returns 
    formatted path
    '''

    output = formatPath( output )
    if os.path.isdir( output ):
        if require_newdir:
            eprint('\nERROR: directory exists.')
            return None
    elif os.path.exists( output ):
        output = os.path.dirname(output)
    else:
        if not mkdir:
            eprint('\nERROR: directory does not exist.')
            return None
        os.mkdir(output)

    if cd:
        os.chdir(output)

    return output


def checkDep( dep_list = [], var_list = [], exempt = set() ):
    '''Checks all dependencies in path from list, optional exemption set'''

    failedVars = []
    check = [ shutil.which( dep ) for dep in dep_list if dep not in exempt ]
    for var in var_list:
        if var not in exempt:
            try:
                os.environ[ var ]
                check.append( True )
            except KeyError:
                check.append( False )
                failedVars.append( var )
    if not all( check ):
        eprint('\nERROR: Dependencies not met:')
        for dep in dep_list:
            if not shutil.which( dep ):
                eprint( dep + ' not in PATH' )
        for failed in failedVars:
            eprint( failed + ' variable not set' )
        sys.exit( 135 )


def file2list( file_, sep = '\n', col = None):
    '''
    Inputs: `file_` path, separator string, column integer index
    Outputs: reads file and returns a list given arguments
    If the `sep` is not valid, return None, else read the file and
    split each line, if `col`, split each by the delimiter, and
    acquire the column index at each line. If not `col`, then 
    simply split by the separator and grab the only entry.
    '''

    if sep not in ['\n', '\t', ',', ' ']:
        eprint('\nERROR: invalid delimiter.')
        return None

    with open(file_, 'r') as raw_data:
        data = raw_data.read() + '\n'

    if col:
        if sep == '\n':
            eprint('\nERROR: cannot split columns by lines')
            return None
        check = data.split('\n')
        check_col = check[0].split(sep).index( col )
        data_list = [ 
            x[check_col].rstrip() for x in [ y.split(sep) for y in check[1:] ] if len(x) >= check_col + 1 
        ]
    else:
        data_list = data.split( sep = sep )
        data_list = [ x.rstrip() for x in data_list if x != '' ]

    return data_list


def multisub( args_lists, processes = 1, shell = False ):
    '''
    Inputs: list of arguments, integer of processes, subprocess `shell` bool
    Outputs: launches and monitors subprocesses and returns list of exit 
    information
    If processes are too few, opt to default. While there are entries in the
    `args_lists`: 
        while there are less entries in `running` than max processes
    and arguments remaining in the `args_lists`: Popen the first argument in 
    the list, append the subprocess information and command to `running` and
    delete the argument from `args_lists`. 
        If there are still args in the args_lists, for each index in running
        grab the handle, poll if it is done, and if it is done output the 
        return code and stdin information to outputs and delete the index
        from `running`.
        IF there are not arguments in args_lists, wait until all processes
        are complete before exiting the function.
    '''

    running, outputs = [ ], []
    if processes <= 0:
        processes = 1
    while len( args_lists ) != 0:
        while len( running ) < processes and len( args_lists ) != 0:
            cmd = args_lists[ 0 ]
            run_temp = subprocess.Popen( cmd, stdout = subprocess.DEVNULL, \
                stderr = subprocess.DEVNULL, shell = shell )
            running.append( [run_temp, cmd ] )
            del args_lists[ 0 ]

        if len( args_lists ) > 0:
            for index in range( len( running ) ):
                handle = running[ index ]
                handle[0].poll()
                returncode = handle[0].returncode
                if returncode is not None:
                    outputs.append( {
                        'stdin': handle[1], 'code': returncode
                        } )
                    del running[ index ]
                    break

        else:
            while len( running ) > 0:
                handle = running[ 0 ]
                handle[0].poll()
                returncode = handle[0].returncode
                if returncode is not None:
                    outputs.append( {
                        'stdin': handle[1], 'code': returncode
                        } )
                    del running[ 0 ]

    return outputs  
