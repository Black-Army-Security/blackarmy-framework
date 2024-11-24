from sqlalchemy.orm import Session
from .models import Target, Subdomain, Port, Service, Vulnerability

# CRUD para Target
def create_target(db: Session, domain: str, ip: str):
    target = Target(domain=domain, ip=ip)
    db.add(target)
    db.commit()
    db.refresh(target)
    return target

def get_target_by_id(db: Session, target_id: int):
    return db.query(Target).filter(Target.id == target_id).first()

def get_all_targets(db: Session):
    return db.query(Target).all()

def update_target(db: Session, target_id: int, domain: str = None, ip: str = None):
    target = db.query(Target).filter(Target.id == target_id).first()
    if target:
        if domain:
            target.domain = domain
        if ip:
            target.ip = ip
        db.commit()
        db.refresh(target)
    return target

def delete_target(db: Session, target_id: int):
    target = db.query(Target).filter(Target.id == target_id).first()
    if target:
        db.delete(target)
        db.commit()

# CRUD para Subdomain
def create_subdomain(db: Session, target_id: int, name: str):
    subdomain = Subdomain(target_id=target_id, name=name)
    db.add(subdomain)
    db.commit()
    db.refresh(subdomain)
    return subdomain

def get_subdomains_by_target(db: Session, target_id: int):
    return db.query(Subdomain).filter(Subdomain.target_id == target_id).all()

# CRUD para Port
def create_port(db: Session, target_id: int, number: int, status: str):
    port = Port(target_id=target_id, number=number, status=status)
    db.add(port)
    db.commit()
    db.refresh(port)
    return port

def get_ports_by_target(db: Session, target_id: int):
    return db.query(Port).filter(Port.target_id == target_id).all()

# CRUD para Service
def create_service(db: Session, port_id: int, name: str, version: str):
    service = Service(port_id=port_id, name=name, version=version)
    db.add(service)
    db.commit()
    db.refresh(service)
    return service

def get_services_by_port(db: Session, port_id: int):
    return db.query(Service).filter(Service.port_id == port_id).all()

# CRUD para Vulnerability
def create_vulnerability(db: Session, target_id: int, description: str, severity: str):
    vulnerability = Vulnerability(target_id=target_id, description=description, severity=severity)
    db.add(vulnerability)
    db.commit()
    db.refresh(vulnerability)
    return vulnerability

def get_vulnerabilities_by_target(db: Session, target_id: int):
    return db.query(Vulnerability).filter(Vulnerability.target_id == target_id).all()

def delete_vulnerability(db: Session, vulnerability_id: int):
    vulnerability = db.query(Vulnerability).filter(Vulnerability.id == vulnerability_id).first()
    if vulnerability:
        db.delete(vulnerability)
        db.commit()
