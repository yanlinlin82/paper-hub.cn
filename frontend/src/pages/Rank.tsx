import { useEffect, useState } from "react";
import {
  useParams,
  useSearchParams,
  Link,
  useNavigate,
} from "react-router";
import api from "../api/client";
import LoadingSpinner from "../components/LoadingSpinner";
import { RankingsResponse } from "../types";

interface RankProps {
  type?: string;
}

function Rank({ type: defaultType }: RankProps) {
  const { groupName, rankType: paramType } = useParams<{
    groupName: string;
    rankType?: string;
  }>();
  const rankType = paramType || defaultType || "this_month";
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [data, setData] = useState<RankingsResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const year = searchParams.get("year") || "";
  const month = searchParams.get("month") || "";

  useEffect(() => {
    const fetchRanks = async () => {
      setLoading(true);
      setError(null);
      try {
        const params: Record<string, string> = {};
        if (year) params.year = year;
        if (month) params.month = month;
        const result = await api.getGroupRankings<RankingsResponse>(
          groupName!,
          rankType,
          params,
        );
        setData(result);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    };
    fetchRanks();
  }, [groupName, rankType, year, month]);

  const handleYearChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const y = e.target.value;
    if (rankType === "yearly") {
      navigate(`/group/${groupName}/rank/${rankType}?year=${y}`);
    } else {
      const m = month || "1";
      navigate(`/group/${groupName}/rank/${rankType}?year=${y}&month=${m}`);
    }
  };

  const handleMonthChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
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
    <div className="d-flex flex-column gap-3">
      {/* Rank type tabs */}
      <ul className="nav nav-pills flex-wrap gap-1">
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

      <div className="card border-0 shadow-sm">
        <div className="card-body">
          {(rankType === "monthly" || rankType === "yearly") && (
            <div className="d-flex flex-wrap justify-content-center gap-2 mb-3">
              <select
                id="yearSelect"
                className="form-select form-select-sm w-auto"
                value={year || data?.year || ""}
                onChange={handleYearChange}
                aria-label="选择年份"
              >
                {data?.year_list?.map((y) => (
                  <option key={y} value={y}>
                    {y}年
                  </option>
                ))}
              </select>
              {rankType === "monthly" && (
                <select
                  className="form-select form-select-sm w-auto"
                  value={month || data?.month || ""}
                  onChange={handleMonthChange}
                  aria-label="选择月份"
                >
                  {data?.month_list?.map((m) => (
                    <option key={m} value={m}>
                      {m}月
                    </option>
                  ))}
                </select>
              )}
            </div>
          )}

          {["this_month", "last_month", "monthly", "yearly"].includes(
            rankType,
          ) && (
            <h5 className="text-center mb-3">
              {rankType === "yearly"
                ? `${data?.year || year}年榜单`
                : `${data?.year || year}年${data?.month || month}月榜单`}
            </h5>
          )}

          {data?.ranks && data.ranks.length > 0 ? (
            <div className="table-responsive">
              <table className="table table-hover align-middle text-center mb-0">
                <thead>
                  <tr>
                    <th style={{ width: "10%" }}>排名</th>
                    <th style={{ width: "40%" }}>
                      {rankType === "journal" ? "杂志" : "分享者"}
                    </th>
                    <th style={{ width: "15%" }}>分享数</th>
                    <th>最早分享时间</th>
                  </tr>
                </thead>
                <tbody>
                  {data.ranks.map((row) => {
                    const getRankBadge = (rank: number) => {
                      if (rank === 1)
                        return (
                          <span className="rank-badge gold">{rank}</span>
                        );
                      if (rank === 2)
                        return (
                          <span className="rank-badge silver">{rank}</span>
                        );
                      if (rank === 3)
                        return (
                          <span className="rank-badge bronze">{rank}</span>
                        );
                      return (
                        <span className="text-body-secondary">{rank}</span>
                      );
                    };
                    return (
                      <tr key={row.display_index}>
                        <td>{getRankBadge(row.display_index)}</td>
                        <td className="text-break" style={{ maxWidth: 0 }}>
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
                        <td>
                          <span className="badge text-bg-primary rounded-pill">
                            {row.count}
                          </span>
                        </td>
                        <td>
                          {row.checkin_at
                            ? (() => {
                                const d = new Date(row.checkin_at);
                                return isNaN(d.getTime())
                                  ? ""
                                  : d.toLocaleString("zh-CN", {
                                      year: "numeric",
                                      month: "2-digit",
                                      day: "2-digit",
                                      hour: "2-digit",
                                      minute: "2-digit",
                                    });
                              })()
                            : ""}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center text-body-secondary py-5">
              暂无数据
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Rank;
