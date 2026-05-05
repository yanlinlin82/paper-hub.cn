import React, { useEffect, useState } from "react";
import {
  useParams,
  useSearchParams,
  Link,
  useNavigate,
} from "react-router-dom";
import api from "../api/client";
import LoadingSpinner from "../components/LoadingSpinner";

function Rank({ type: defaultType }) {
  const { groupName, rankType: paramType } = useParams();
  const rankType = paramType || defaultType || "this_month";
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const year = searchParams.get("year") || "";
  const month = searchParams.get("month") || "";

  useEffect(() => {
    const fetchRanks = async () => {
      setLoading(true);
      setError(null);
      try {
        const params = {};
        if (year) params.year = year;
        if (month) params.month = month;
        const result = await api.getGroupRankings(groupName, rankType, params);
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchRanks();
  }, [groupName, rankType, year, month]);

  const handleYearChange = (e) => {
    const y = e.target.value;
    if (rankType === "yearly") {
      navigate(`/group/${groupName}/rank/${rankType}?year=${y}`);
    } else {
      const m = month || "1";
      navigate(`/group/${groupName}/rank/${rankType}?year=${y}&month=${m}`);
    }
  };

  const handleMonthChange = (e) => {
    const m = e.target.value;
    navigate(
      `/group/${groupName}/rank/${rankType}?year=${year || data?.year || 2024}&month=${m}`,
    );
  };

  const tabs = [
    { label: "本月榜单", type: "this_month" },
    { label: "上月榜单", type: "last_month" },
    { label: "月度榜单", type: "monthly" },
    { label: "年度榜单", type: "yearly" },
    { label: "总榜单", type: "all" },
    { label: "杂志榜单", type: "journal" },
  ];

  if (loading) return <LoadingSpinner />;
  if (error) return <div className="alert alert-danger">{error}</div>;

  return (
    <div>
      <ul className="nav rank-tabs">
        {tabs.map((tab) => (
          <li key={tab.type} className="nav-item">
            <Link
              className={`nav-link${rankType === tab.type ? " active" : ""}`}
              to={`/group/${groupName}/rank/${tab.type}`}
            >
              {tab.label}
            </Link>
          </li>
        ))}
      </ul>

      <div className="rank-content">
        {(rankType === "monthly" || rankType === "yearly") && (
          <form className="mt-3 mx-auto col-12 col-md-6 col-lg-4 col-xl-3">
            <div className="input-group w-auto mb-3">
              <select
                id="yearSelect"
                className="form-select form-select-sm"
                value={year || data?.year || ""}
                onChange={handleYearChange}
              >
                {data?.year_list?.map((y) => (
                  <option key={y} value={y}>
                    {y}
                  </option>
                ))}
              </select>
              {rankType === "monthly" && (
                <>
                  &nbsp;
                  <select
                    className="form-select form-select-sm"
                    value={month || data?.month || ""}
                    onChange={handleMonthChange}
                  >
                    {data?.month_list?.map((m) => (
                      <option key={m} value={m}>
                        {m}
                      </option>
                    ))}
                  </select>
                </>
              )}
            </div>
          </form>
        )}

        {["this_month", "last_month", "monthly", "yearly"].includes(
          rankType,
        ) && (
          <div className="text-center fw-bold my-3">
            {rankType === "yearly"
              ? `${data?.year || year}年榜单`
              : `${data?.year || year}年${data?.month || month}月榜单`}
          </div>
        )}

        {data?.ranks && data.ranks.length > 0 ? (
          <table className="rank-table text-center">
            <thead>
              <tr>
                <th>排名</th>
                <th>{rankType === "journal" ? "杂志" : "分享者"}</th>
                <th>分享数</th>
                <th>最早分享时间</th>
              </tr>
            </thead>
            <tbody>
              {data.ranks.map((row) => {
                const getRankBadge = (rank) => {
                  if (rank === 1)
                    return <span className="rank-badge gold">{rank}</span>;
                  if (rank === 2)
                    return <span className="rank-badge silver">{rank}</span>;
                  if (rank === 3)
                    return <span className="rank-badge bronze">{rank}</span>;
                  return rank;
                };
                return (
                  <tr key={row.display_index}>
                    <td>{getRankBadge(row.display_index)}</td>
                    <td>
                      {rankType === "journal" ? (
                        <Link
                          to={`/group/${groupName}/journal/${encodeURIComponent(row.name)}`}
                        >
                          {row.name}
                        </Link>
                      ) : (
                        <Link to={`/group/${groupName}/user/${row.id}`}>
                          {row.name}
                        </Link>
                      )}
                    </td>
                    <td>{row.count}</td>
                    <td>{new Date(row.create_time).toLocaleString("zh-CN")}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        ) : (
          <div className="card-body text-center my-5">暂无数据</div>
        )}
      </div>
    </div>
  );
}

export default Rank;
