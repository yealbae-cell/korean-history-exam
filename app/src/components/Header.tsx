import { Link, useLocation } from 'react-router-dom';
import styled from 'styled-components';

const navItems = [
  { path: '/', label: '홈' },
  { path: '/wrong-answers', label: '오답노트' },
  { path: '/stats', label: '통계' },
];

export default function Header() {
  const location = useLocation();

  return (
    <HeaderBar>
      <Logo to="/">한국사 기출마스터</Logo>
      <Nav>
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            $active={location.pathname === item.path}
          >
            {item.label}
          </NavLink>
        ))}
      </Nav>
    </HeaderBar>
  );
}

const HeaderBar = styled.header`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: #1971c2;
  color: #fff;
  position: sticky;
  top: 0;
  z-index: 100;
`;

const Logo = styled(Link)`
  font-size: 20px;
  font-weight: 800;
  color: #fff;
  text-decoration: none;
`;

const Nav = styled.nav`
  display: flex;
  gap: 8px;
`;

const NavLink = styled(Link)<{ $active: boolean }>`
  padding: 6px 14px;
  border-radius: 6px;
  color: #fff;
  text-decoration: none;
  font-weight: 500;
  font-size: 14px;
  background: ${(p) => (p.$active ? 'rgba(255,255,255,0.2)' : 'transparent')};

  &:hover {
    background: rgba(255, 255, 255, 0.15);
  }
`;
