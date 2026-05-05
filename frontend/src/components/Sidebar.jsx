import React from "react";
import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import CheckInButton from "./CheckInButton";

function Sidebar({ groupName }) {
  const { user } = useAuth();

  const linkClass = ({ isActive }) =>
    `list-group-item list-group-item-action ${isActive ? "active" : ""}`;

  return (
    <div className="sidebar">
      {user && <CheckInButton groupName={groupName} />}
      <div className="list-group text-center my-3">
        <div className="list-group-item list-group-item-dark">响马读paper</div>
        <NavLink to={`/group/${groupName}`} end className={linkClass}>
          社群首页
        </NavLink>
        {user && (
          <NavLink to={`/group/${groupName}/my_sharing`} className={linkClass}>
            我的分享
          </NavLink>
        )}
        <NavLink to={`/group/${groupName}/all`} className={linkClass}>
          所有分享
        </NavLink>
        <NavLink to={`/group/${groupName}/this_month`} className={linkClass}>
          本月分享
        </NavLink>
        <NavLink to={`/group/${groupName}/last_month`} className={linkClass}>
          上月分享
        </NavLink>
        <NavLink to={`/group/${groupName}/rank`} className={linkClass}>
          社群榜单
        </NavLink>
        {user && (
          <NavLink to={`/group/${groupName}/trash`} className={linkClass}>
            回收站
          </NavLink>
        )}
      </div>
    </div>
  );
}

export default Sidebar;
