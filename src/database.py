"""Criação do banco, sessão e operações CRUD."""
from __future__ import annotations
from contextlib import contextmanager
from typing import Any, Generator
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from .models import Base, Atendimento

def create_session_factory(url: str) -> sessionmaker:
    """Cria as tabelas do banco e retorna uma fábrica de sessões."""
    engine = create_engine(url, future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)

@contextmanager
def session_scope(factory: sessionmaker) -> Generator[Session, None, None]:
    """Gerencia uma sessão de banco com commit, rollback e fechamento."""
    session: Session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def find_by_protocol(session: Session, protocol: str) -> Atendimento | None:
    """Busca um atendimento pelo protocolo informado."""
    return session.scalar(select(Atendimento).where(Atendimento.protocolo == protocol))
    
def delete_by_protocol(session: Session, protocol: str) -> bool:
    """Exclui um atendimento pelo protocolo e informa se ele foi encontrado."""
    item = find_by_protocol(session, protocol)
    if not item:
        return False
    session.delete(item)
    return True

def update_by_protocol(session: Session, protocol: str, **fields: Any) -> Atendimento | None:
    """Atualiza os campos informados de um atendimento identificado pelo protocolo."""
    item = find_by_protocol(session, protocol)
    if not item:
        return None

    for key, value in fields.items():
        if hasattr(item, key):
            setattr(item, key, value)

    session.flush()
    return item