from sqlalchemy import Column, Integer, String, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Target(Base):
    __tablename__ = 'targets'
    id = Column(Integer, primary_key=True)
    domain = Column(String(255), nullable=False)
    ip = Column(String(255))
    os = Column(String(255))
    waf = Column(String(255))
    subdomains = relationship('Subdomain', back_populates='target')
    dns_records = relationship('DnsRecord', back_populates='target')


class Subdomain(Base):
    __tablename__ = 'subdomains'
    id = Column(Integer, primary_key=True)
    target_id = Column(Integer, ForeignKey('targets.id'))
    subdomain = Column(String(255), nullable=False)
    ip = Column(String(255))
    target = relationship('Target', back_populates='subdomains')
    ports = relationship('Port', back_populates='subdomain')


class Port(Base):
    __tablename__ = 'ports'
    id = Column(Integer, primary_key=True)
    subdomain_id = Column(Integer, ForeignKey('subdomains.id'))
    port = Column(Integer, nullable=False)
    protocol = Column(String(10), nullable=False)
    state = Column(String(10), nullable=False)
    subdomain = relationship('Subdomain', back_populates='ports')
    services = relationship('Service', back_populates='port')


class Service(Base):
    __tablename__ = 'services'
    id = Column(Integer, primary_key=True)
    port_id = Column(Integer, ForeignKey('ports.id'))
    service_name = Column(String(255), nullable=False)
    version = Column(String(255))
    port = relationship('Port', back_populates='services')
    vulnerabilities = relationship('Vulnerability', back_populates='service')


class Vulnerability(Base):
    __tablename__ = 'vulnerabilities'
    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey('services.id'))
    vulnerability = Column(Text, nullable=False)
    severity = Column(String(50))
    cve_id = Column(String(50))
    service = relationship('Service', back_populates='vulnerabilities')


class DnsRecord(Base):
    __tablename__ = 'dns_records'
    id = Column(Integer, primary_key=True)
    target_id = Column(Integer, ForeignKey('targets.id'))
    record_type = Column(Enum('A', 'CNAME', 'NS', 'MX', 'TXT', 'SOA', 'SRV', 'PTR', 'AAAA', name='dns_record_types'), nullable=False)
    value = Column(String(255), nullable=False)
    target = relationship('Target', back_populates='dns_records')
