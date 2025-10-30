from pathlib import Path

class Config:
    """
    Customized basic Config as a class to store paths to key files and data in the project. The idea is simple: most data projects
    need a dedicated data/ folder for datasets, processed files, models and so on. To prevent code from breaking when paths change,
    we wrap all important locations in this object.

    You can manage folders under data/ by passing custom paths at object creation. If you want to add new folders beyond the default
    01–07 structure, simply add them to self._config. For any folder that should be overridable at creation time, use the helper
    function override_or_default inside __init__: it checks if a custom path was provided, otherwise uses the default, and always
    creates the directory if missing. This avoids repeating the same “check or create” logic for every folder.

    In short, Config centralizes and safeguards all project paths, while override_or_default makes it easy to override defaults
    and guarantees the corresponding directories exist.
    """
    def __init__(self, base_dir: Path = None, indexer_dir: Path=None, **custom_paths):
        self.base_dir = base_dir or Path(__file__).resolve().parents[3] / 'data' # store all data in dedicated folder ⚠️
        self.indexer_dir = base_dir or Path(__file__).resolve().parents[3] / '.index' # store all data in dedicated folder ⚠️
        print(f'Config initialized with \n base_dir: {self.base_dir}')
        '''
        Supposed config will be stored at src/helpers/config.py
        Rules of devine config:
        1. Don't change variables names, only path.
        2. If you change path, it's up to you, but remember it's never late to turn back
        3. Configs sorted vice versa on purpose.
        Due to expecation you will like to change them as less
        as you get closer to raw data.

        Instance of usage:
        cfg = Config(
            base_dir=Path("my_data_folder"),
            raw_dir=Path("/mnt/drive/datasets/raw"),
            logs_dir=Path("/tmp/logs")
        )
        config.get('cleaned_dir')

        In this case you will have all dirs stored at base dir, except of those you redifined to other folders

        When you move config to new project and don't use custom paths, just change default value for base dir. 


        All commented lines means some config path aren't used in project currently, but might be used in the future. All uncommented paths are used.
        '''

        def override_or_default(key: str, default: Path):
            path =  Path(custom_paths.get(key, default)) # if key exists in custom_path - return it as path, else take 'defatult' var
            path.mkdir(parents=True, exist_ok=True)
            return path


        # Sub data/ folders
        logs_dir      = override_or_default('logs_dir', self.base_dir / '07_logs')
        predict_dir   = override_or_default('predict_dir', self.base_dir / '06_predictions')
        processed_dir = override_or_default('processed_dir', self.base_dir / '05_processed')
        features_dir  = override_or_default('features_dir', self.base_dir / '04_features')
        validated_dir = override_or_default('validated_dir', self.base_dir / '03_validated')
        cleaned_dir   = override_or_default('cleaned_dir', self.base_dir / '02_cleaned')
        raw_dir       = override_or_default('raw_dir', self.base_dir / '01_raw')
        indexer_dir   = override_or_default('indexer_dir', self.indexer_dir)
        
        self._config = {
            # Logs_07
            'logs_dir':                   logs_dir,
            'logs_db':                    logs_dir / 'logs.db',
            # Indexer
            'indexer_dir':                indexer_dir,
            'index_file':                 indexer_dir / 'index.faiss',
            'chunks_file':                indexer_dir / 'chunks.pkl',

            # Validated_3
            'validated_dir':              validated_dir,
            'all_documents_dump':         validated_dir / 'all_documents_dump.txt', # used at qabot/evals

            # Cleaned_02
            'cleaned_dir':                cleaned_dir,

            # Raw _01
            'raw_dir':                    raw_dir,
            'canonical_dir':              raw_dir / 'it-knowledge' / 'canonical',
            'questions':                  raw_dir / 'golden_path' / 'questions.csv',
            'questions_advanced':         raw_dir / 'golden_path' /'questions_advanced.csv'
        }

    def get(self, key : str) -> Path:
            if key not in self._config:
                raise KeyError(f"Config key '{key}' not found.\nPossible keys: {self.keys()}")
            return self._config[key]

    def set(self, key: str, value: Path | str) -> None:
            if 'dir' in key:
                raise KeyError(f'You can set base directories only when creating config object')
            self._config[key] = Path(value)
    

    def as_dict(self) -> dict[str, Path]:
          return self._config.copy()

    def keys(self) -> list[str]:
          return list(self._config.keys())

    def __setitem__(self, key: str, value: Path | str) -> None:
        if 'dir' in key:
            raise KeyError(f'You can set base directories only when creating config object')
        self._config[key] = Path(value)

    def __getitem__(self, key: str) -> Path:
        return self.get(key)                                             # To have possibility call keys through dict syntax e.g. config['key']

    def __contains__(self, key: str) -> bool:
        return key in self._config                                       # To support expressions as " if 'key' in config "

    def __repr__(self) -> str:
          return '\n'.join(f"{k}: {v}" for k, v in self._config.items()) # To use syntax as "print(config)"
