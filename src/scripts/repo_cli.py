import argparse
import sqlite3
from contextlib import contextmanager

from src.qabot.helpers.config import Config
from src.qabot.repository.document_repository import DocumentRepository
from src.qabot.repository.chunk_repository import ChunkRepository
from src.qabot.repository.models import DocumentRecord, ChunkRecord


@contextmanager
def _connect(db_path):
    conn = sqlite3.connect(db_path, check_same_thread=False)
    try:
        conn.row_factory = sqlite3.Row
        yield conn
    finally:
        conn.close()


def _resolve_db_path(config: Config, table: str, override: str | None):
    if override:
        return override
    if table == "documents":
        return config["documents_db"]
    return config["chunks_db"]


def _fetch_all(conn, table: str):
    cur = conn.execute(f"SELECT * FROM {table}")
    return cur.fetchall()


def _rows_to_records(table: str, rows):
    if table == "documents":
        return [DocumentRecord(**dict(row)) for row in rows]
    return [ChunkRecord(**dict(row)) for row in rows]


def _print_records(records):
    if records is None:
        print("not found")
        return
    if isinstance(records, list):
        for record in records:
            print(record.to_dict())
        return
    print(records.to_dict())


def _handle_get(args, config: Config):
    db_path = _resolve_db_path(config, args.table, args.db)
    with _connect(db_path) as conn:
        if args.table == "documents":
            repo = DocumentRepository(conn)
            repo._ensure_schema()
            if args.id is not None:
                _print_records(repo.get_by_doc_id(args.id))
                return
            if args.source_uri:
                _print_records(repo.get_by_source_uri(args.source_uri))
                return
            rows = _fetch_all(conn, "documents")
            _print_records(_rows_to_records("documents", rows))
            return

        repo = ChunkRepository(conn)
        repo._ensure_schema()
        if args.id is not None:
            if hasattr(repo, "get_by_chunk_id"):
                _print_records(repo.get_by_chunk_id(args.id))
                return
            cur = conn.execute("SELECT * FROM chunks WHERE chunk_id = ?", (args.id,))
            row = cur.fetchone()
            _print_records(ChunkRecord(**dict(row)) if row else None)
            return
        if args.doc_id is not None:
            if hasattr(repo, "get_by_doc_id"):
                _print_records(repo.get_by_doc_id(args.doc_id))
                return
            cur = conn.execute("SELECT * FROM chunks WHERE doc_id = ?", (args.doc_id,))
            rows = cur.fetchall()
            _print_records(_rows_to_records("chunks", rows))
            return
        rows = _fetch_all(conn, "chunks")
        _print_records(_rows_to_records("chunks", rows))


def _handle_delete(args, config: Config):
    db_path = _resolve_db_path(config, args.table, args.db)
    with _connect(db_path) as conn:
        if args.table == "documents":
            repo = DocumentRepository(conn)
            repo._ensure_schema()
            if args.id is not None:
                deleted = repo.delete(args.id)
            elif args.source_uri:
                if hasattr(repo, "delete_by_source_uri"):
                    deleted = repo.delete_by_source_uri(args.source_uri)
                else:
                    cur = conn.execute(
                        "DELETE FROM documents WHERE source_uri = ?",
                        (args.source_uri,),
                    )
                    conn.commit()
                    deleted = cur.rowcount
            else:
                raise SystemExit("documents delete requires --id or --source-uri")
        else:
            repo = ChunkRepository(conn)
            repo._ensure_schema()
            if args.id is not None:
                deleted = repo.delete(args.id)
            elif args.doc_id is not None:
                if hasattr(repo, "delete_by_doc_id"):
                    deleted = repo.delete_by_doc_id(args.doc_id)
                else:
                    cur = conn.execute("DELETE FROM chunks WHERE doc_id = ?", (args.doc_id,))
                    conn.commit()
                    deleted = cur.rowcount
            else:
                raise SystemExit("chunks delete requires --id or --doc-id")
        print(f"deleted: {deleted}")


def _build_parser():
    parser = argparse.ArgumentParser(description="Repo CLI for documents/chunks.")
    parser.add_argument("--db", help="Override sqlite db path (optional)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    get_parser = subparsers.add_parser("get", help="Get records")
    get_parser.add_argument("--table", required=True, choices=["documents", "chunks"])
    get_parser.add_argument("--id", type=int, help="doc_id or chunk_id")
    get_parser.add_argument("--doc-id", type=int, help="Filter chunks by doc_id")
    get_parser.add_argument("--source-uri", help="Filter documents by source_uri")

    delete_parser = subparsers.add_parser("delete", help="Delete records")
    delete_parser.add_argument("--table", required=True, choices=["documents", "chunks"])
    delete_parser.add_argument("--id", type=int, help="doc_id or chunk_id")
    delete_parser.add_argument("--doc-id", type=int, help="Delete chunks by doc_id")
    delete_parser.add_argument("--source-uri", help="Delete documents by source_uri")

    return parser


def main():
    parser = _build_parser()
    args = parser.parse_args()
    config = Config()

    if args.command == "get":
        _handle_get(args, config)
    elif args.command == "delete":
        _handle_delete(args, config)
    else:
        raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
