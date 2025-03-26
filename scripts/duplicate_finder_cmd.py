import settings
import init
import archive


def main():
    settings.Config._read_settings()
    cleaner_archives()
    catalog = archive.Archive()
    catalog.search_new_file()



def cleaner_archives():
    print(settings.FolderName.data)
    print(settings.PathFile.batches_self_tested)
    print(settings.Config.path)
    print("duplicate_finder")


main()