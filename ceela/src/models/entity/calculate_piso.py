from sqlmodel import SQLModel, Field
from typing import Optional


class CalculatePiso(SQLModel, table=True):
    __tablename__="calculate_piso"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    enclosure_id: int
    floor_id: int
    b: float
    rf: float
    df: float
    ufg_sog: float
    psi: float
    u_vert: float
    rn_vert: float
    dn_vert: float
    r_vertical: float
    d_vertical: float
    psi_vertical: float
    u_horiz: float
    rn_horiz: float
    dn_horiz: float
    r_horiz: float
    d_horiz: float
    psi_horiz: float
    psi_min: float
    ls: float