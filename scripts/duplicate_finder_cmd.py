import settings
import init


def main():
    settings.Config._read_settings()
    cleaner_archives()


def cleaner_archives():
    print(settings.FolderName.data)
    print(settings.PathFile.batches_self_tested)
    print(settings.Config.path)
    print("duplicate_finder")


main()