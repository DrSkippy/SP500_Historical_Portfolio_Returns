if __name__ == "__main__":
    import glob
    import sys
    from returns.data import *

    # Configure logging
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S",
                        stream=sys.stdout,
                        filemode="w")
    create_combined_data_file()
    files = glob.glob("./out_data/returns_*.csv")
    files_created = create_summary_files(files)
    logger.info(f"Summary files created: {files_created}")
    logger.info("Done")
