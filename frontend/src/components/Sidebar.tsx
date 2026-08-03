import { NavLink } from "react-router";
import { useAuth } from "../context/AuthContext";
import CheckInButton from "./CheckInButton";

interface SidebarProps {
  groupName: string | undefined;
}

function Sidebar({ groupName }: SidebarProps) {
  const { user } = useAuth();

  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `nav-link d-flex align-items-center gap-2${isActive ? " active" : ""}`;

  const links = [
    { to: `/group/${groupName}`, label: "社群首页", end: true, show: true },
    { to: `/group/${groupName}/my_sharing`, label: "我的分享", show: !!user },
    { to: `/group/${groupName}/all`, label: "所有分享", show: true },
    { to: `/group/${groupName}/this_month`, label: "本月分享", show: true },
    { to: `/group/${groupName}/last_month`, label: "上月分享", show: true },
    { to: `/group/${groupName}/rank`, label: "社群榜单", show: true },
    { to: `/group/${groupName}/trash`, label: "回收站", show: !!user },
    {
      to: `/group/${groupName}/custom-checkin-interval-config`,
      label: "打卡时间配置",
      show: !!user?.is_superuser,
    },
  ];

  return (
    <nav className="d-flex flex-column gap-3">
      {user && <CheckInButton groupName={groupName} />}

      <div className="card border-0 shadow-sm">
        <div className="card-body py-3">
          <h6 className="card-title text-body-secondary text-uppercase small fw-semibold mb-2 px-2">
            导航
          </h6>
          <ul className="nav nav-pills flex-column gap-1">
            {links
              .filter((l) => l.show)
              .map((l) => (
                <li key={l.to} className="nav-item">
                  <NavLink to={l.to} end={l.end} className={linkClass}>
                    {l.label}
                  </NavLink>
                </li>
              ))}
          </ul>
        </div>
      </div>
    </nav>
  );
}

export default Sidebar;
