import os
import shutil

def main():
    dest_dir = "assets/images"
    
    # Map failed ones to local copies
    copy_map = {
        "coorg.jpg": "nature.jpg",
        "hampi.jpg": "heritage.jpg"
    }
    
    for dest_name, src_name in copy_map.items():
        src_path = os.path.join(dest_dir, src_name)
        dest_path = os.path.join(dest_dir, dest_name)
        if os.path.exists(src_path):
            shutil.copy(src_path, dest_path)
            print(f"Copied local {src_name} to {dest_path}")
        else:
            print(f"Source file {src_path} does not exist!")

if __name__ == "__main__":
    main()
