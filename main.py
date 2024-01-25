import json
import os
import subprocess
import zlib

UESAVE_TYPE_MAPS = [
    ".worldSaveData.CharacterSaveParameterMap.Key=Struct",
    ".worldSaveData.FoliageGridSaveDataMap.Key=Struct",
    ".worldSaveData.FoliageGridSaveDataMap.ModelMap.InstanceDataMap.Key=Struct",
    ".worldSaveData.MapObjectSpawnerInStageSaveData.Key=Struct",
    ".worldSaveData.ItemContainerSaveData.Key=Struct",
    ".worldSaveData.CharacterContainerSaveData.Key=Struct",
]


def main():
    # Warn the user about potential data loss.
    print('WARNING: Running this script WILL change your save files and could \
potentially corrupt your data. It is HIGHLY recommended that you make a backup \
of your save folder before continuing.')
    input('> Press Enter to Continue')
    
    uesave_path = input("\nEnter your uesave .exe path\n> ") # Usually C:\\Program Files\\uesave\\bin\\uesave.exe
    old_character = input("\nPath to EXISTING character\n> ")
    new_character = input("\nPath to NEW character with NEW appearance\n> ")

    old_character_json = old_character + '.json'
    new_character_json = new_character + '.json'

    # uesave_path must point directly to the executable, not just the path it is located in.
    if not os.path.exists(uesave_path) or not os.path.isfile(uesave_path):
        print('ERROR: Your given <uesave_path> of "' + uesave_path + '" is invalid. It must point directly to the executable. For example: C:\\Users\\Bob\\.cargo\\bin\\uesave.exe')
        exit(1)
    
    # old_character must exist in order to use it.
    if not os.path.exists(old_character):
        print('ERROR: Your given <old_character> of "' + old_character + '" does not exist. Did you enter the correct path to your player save?')
        exit(1)
    # new_character must exist in order to use it.
    if not os.path.exists(new_character):
        print(
            'ERROR: Your given <new_character> of "' + new_character + '" does not exist. Did you enter the correct path to your player save?')
        exit(1)
    
    # Convert player files to JSON so it is possible to edit them.
    sav_to_json(uesave_path, old_character)
    sav_to_json(uesave_path, new_character)
    print('Converted player files to JSON')

    # Parse our JSON files.
    with open(old_character_json) as f:
        old_json = json.load(f)
    with open(new_character_json) as f:
        new_json = json.load(f)
    print('JSON files have been parsed')

    old_json['root']['properties']['SaveData']['Struct']['value']['Struct']['PlayerCharacterMakeData'] = new_json['root']['properties']['SaveData']['Struct']['value']['Struct']['PlayerCharacterMakeData']
    print("Appearance changes have been made")
    
    # Dump modified data to JSON.
    with open(old_character_json, 'w') as f:
        json.dump(old_json, f, indent=2)
    print('JSON files have been exported')

    # Convert our JSON files to save files.
    json_to_sav(uesave_path, old_character_json)
    print('Converted JSON files back to save files')

    # Clean up miscellaneous GVAS and JSON files which are no longer needed.
    clean_up_files(old_character)
    clean_up_files(new_character)
    print('Miscellaneous files removed')

    print('\nNew appearance applied! Have fun!')


def sav_to_json(uesave_path, file):
    with open(file, 'rb') as f:
        # Read the file
        data = f.read()
        uncompressed_len = int.from_bytes(data[0:4], byteorder='little')
        compressed_len = int.from_bytes(data[4:8], byteorder='little')
        magic_bytes = data[8:11]
        save_type = data[11]
        # Check for magic bytes
        if magic_bytes != b'PlZ':
            print(f'File {file} is not a save file, found {magic_bytes} instead of P1Z')
            return
        # Valid save types
        if save_type not in [0x30, 0x31, 0x32]:
            print(f'File {file} has an unknown save type: {save_type}')
            return
        # We only have 0x31 (single zlib) and 0x32 (double zlib) saves
        if save_type not in [0x31, 0x32]:
            print(f'File {file} uses an unhandled compression type: {save_type}')
            return
        if save_type == 0x31:
            # Check if the compressed length is correct
            if compressed_len != len(data) - 12:
                print(f'File {file} has an incorrect compressed length: {compressed_len}')
                return
        # Decompress file
        uncompressed_data = zlib.decompress(data[12:])
        if save_type == 0x32:
            # Check if the compressed length is correct
            if compressed_len != len(uncompressed_data):
                print(f'File {file} has an incorrect compressed length: {compressed_len}')
                return
            # Decompress file
            uncompressed_data = zlib.decompress(uncompressed_data)
        # Check if the uncompressed length is correct
        if uncompressed_len != len(uncompressed_data):
            print(f'File {file} has an incorrect uncompressed length: {uncompressed_len}')
            return
        # Save the uncompressed file
        with open(file + '.gvas', 'wb') as f:
            f.write(uncompressed_data)
        print(f'File {file} uncompressed successfully')
        # Convert to json with uesave
        # Run uesave.exe with the uncompressed file piped as stdin
        # Standard out will be the json string
        uesave_run = subprocess.run(uesave_to_json_params(uesave_path, file+'.json'), input=uncompressed_data, capture_output=True)
        # Check if the command was successful
        if uesave_run.returncode != 0:
            print(f'uesave.exe failed to convert {file} (return {uesave_run.returncode})')
            print(uesave_run.stdout.decode('utf-8'))
            print(uesave_run.stderr.decode('utf-8'))
            return
        print(f'File {file} (type: {save_type}) converted to JSON successfully')


def json_to_sav(uesave_path, file):
    # Convert the file back to binary
    gvas_file = file.replace('.sav.json', '.sav.gvas')
    sav_file = file.replace('.sav.json', '.sav')
    uesave_run = subprocess.run(uesave_from_json_params(uesave_path, file, gvas_file))
    if uesave_run.returncode != 0:
        print(f'uesave.exe failed to convert {file} (return {uesave_run.returncode})')
        return
    # Open the old sav file to get type
    with open(sav_file, 'rb') as f:
        data = f.read()
        save_type = data[11]
    # Open the binary file
    with open(gvas_file, 'rb') as f:
        # Read the file
        data = f.read()
        uncompressed_len = len(data)
        compressed_data = zlib.compress(data)
        compressed_len = len(compressed_data)
        if save_type == 0x32:
            compressed_data = zlib.compress(compressed_data)
        with open(sav_file, 'wb') as f:
            f.write(uncompressed_len.to_bytes(4, byteorder='little'))
            f.write(compressed_len.to_bytes(4, byteorder='little'))
            f.write(b'PlZ')
            f.write(bytes([save_type]))
            f.write(bytes(compressed_data))
    print(f'Converted {file} to {sav_file}')


def clean_up_files(file):
    os.remove(file + '.json')
    os.remove(file + '.gvas')


def uesave_to_json_params(uesave_path, out_path):
    args = [
        uesave_path,
        'to-json',
        '--output', out_path,
    ]
    for map_type in UESAVE_TYPE_MAPS:
        args.append('--type')
        args.append(f'{map_type}')
    return args


def uesave_from_json_params(uesave_path, input_file, output_file):
    args = [
        uesave_path,
        'from-json',
        '--input', input_file,
        '--output', output_file,
    ]
    return args


if __name__ == "__main__":
    main()
