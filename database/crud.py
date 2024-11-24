from sqlalchemy.orm import Session
from .models import Target, Subdomain, Port, Service, Vulnerability, DnsRecord

# CREATE: Adicionar dados no banco de dados
def create_target(session: Session, domain: str, ip: str = None, os: str = None, waf: str = None) -> Target:
    target = Target(domain=domain, ip=ip, os=os, waf=waf)
    session.add(target)
    session.commit()
    session.refresh(target)
    return target

def create_subdomain(session: Session, target_id: int, subdomain: str, ip: str = None) -> Subdomain:
    sub = Subdomain(target_id=target_id, subdomain=subdomain, ip=ip)
    session.add(sub)
    session.commit()
    session.refresh(sub)
    return sub

def create_port(session: Session, subdomain_id: int, port: int, protocol: str, state: str) -> Port:
    port_entry = Port(subdomain_id=subdomain_id, port=port, protocol=protocol, state=state)
    session.add(port_entry)
    session.commit()
    session.refresh(port_entry)
    return port_entry

# READ: Consultar dados no banco de dados
def get_target_by_domain(session: Session, domain: str) -> Target:
    return session.query(Target).filter(Target.domain == domain).first()

def get_all_targets(session: Session):
    return session.query(Target).all()

# UPDATE: Atualizar informações
def update_target_waf(session: Session, target_id: int, new_waf: str):
    target = session.query(Target).filter(Target.id == target_id).first()
    if target:
        target.waf = new_waf
        session.commit()
    return target

# DELETE: Remover entradas
def delete_target(session: Session, target_id: int):
    target = session.query(Target).filter(Target.id == target_id).first()
    if target:
        session.delete(target)
        session.commit()
        return True
    return False
