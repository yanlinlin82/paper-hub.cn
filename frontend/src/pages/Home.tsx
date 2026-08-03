import { useEffect, useState } from "react";
import { useParams } from "react-router";
import { GroupInfo } from "../types";

interface RuleItem {
  title: string;
  items: string[];
}

const RULES: RuleItem[] = [
  {
    title: "学术交流",
    items: [
      "本群为学术交流群，禁止广告、政治言论和不当言论，违规者立即踢出群。",
      "不强制实名，但为确保统计正确，建议保持昵称稳定。",
      "倡导敢于质疑、敢于不拘一格的“响马”精神，勇于挑战自我。",
    ],
  },
  {
    title: "每月打卡",
    items: [
      "每月需读完1篇正式发表的学术论文，撰写推荐理由、评论或解读，并在群内打卡，首月可豁免。",
      "每月1日检查上月打卡情况，未完成者将被移出群，离群一个月后可重新申请入群。",
    ],
  },
  {
    title: "打卡方式",
    items: [
      "在微信群中，通过输入以“#paper”开头的文字信息进行打卡，建议格式为：“#paper doi 杂志, 年份, 标题。推荐理由”，如无doi，可用其它唯一标识（如arXivID、PMID或PMCID）注明，以便他人查找。",
      "微信群打卡信息将由群主手动同步到网站，因此可能会有一定延迟。",
    ],
  },
  {
    title: "论文分享",
    items: [
      "所有正式发表的学术论文均可分享，专业不限。内容需符合打卡格式，观点仅代表分享者个人。",
      "欢迎成员对分享的论文展开讨论，促进学科间交流。",
    ],
  },
  {
    title: "打卡查询",
    items: [
      "通过微信群聊天记录搜索“#paper”关键字进行查询。",
      "也可浏览本网站，查看各期打卡情况及排名。",
      "如有统计错误，请联系群主解决。",
    ],
  },
  {
    title: "社群发展",
    items: ["本群成立于2022年1月8日，目标是坚持读paper，一起精进60年。"],
  },
];

interface SessionItem {
  date: string;
  title: string;
  url?: string;
  note?: string;
}

const SESSIONS: SessionItem[] = [
  {
    date: "2024-07-12",
    title: "李翛然：全球首次真实量子计算的药物设计过程分享",
    note: "因部分内容暂不便大规模公开，故此次分享未录屏，没有回放",
  },
  {
    date: "2022-11-12",
    title: "林海：Alpha智能体家族的进化与应用之路",
    url: "https://www.bilibili.com/video/BV1PD4y147gK/",
  },
  {
    date: "2022-10-22",
    title: "王昊：视觉问答算法简介",
    url: "https://www.bilibili.com/video/BV1jW4y1E7fr/",
  },
  {
    date: "2022-09-17",
    title: "尹志：对比学习图像翻译",
    url: "https://www.bilibili.com/video/BV1nW4y1q7ja/",
  },
  {
    date: "2022-09-03",
    title: "曾梓龙：基于变分自编码器的动态多因子模型",
    url: "https://www.bilibili.com/video/BV1fY4y1T7rq/",
  },
  {
    date: "2022-08-13",
    title: "林海：Quantum-Reinforcement-Learning",
    url: "https://www.bilibili.com/video/BV1Ld4y1K7nh/",
  },
  {
    date: "2022-08-06",
    title: "尹志：AI-based-Pathology-Biomarkers",
    url: "https://www.bilibili.com/video/BV1RV4y1j7UF/",
  },
  {
    date: "2022-07-23",
    title: "颜林林：用DNA分子实现生物计算机",
    url: "https://www.bilibili.com/video/BV1ug4111728/",
  },
  {
    date: "2022-07-09",
    title: "曾梓龙：利用深度学习研究自闭症的神经解剖学变异",
    url: "https://www.bilibili.com/video/BV1tZ4y1Y79a/",
  },
  {
    date: "2022-06-28",
    title: "大象城南：神经纤维追踪算法",
    note: "因第一次活动未录屏，故没有回放",
  },
];

function Home() {
  const { groupName } = useParams<{ groupName: string }>();
  const [groupInfo, setGroupInfo] = useState<GroupInfo | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    if (groupName && groupName !== "xiangma") {
      const fetchGroup = async () => {
        try {
          const api = (await import("../api/client")).default;
          const info = await api.getGroupInfo<GroupInfo>(groupName);
          setGroupInfo(info);
        } catch {
          setGroupInfo(null);
        } finally {
          setLoading(false);
        }
      };
      fetchGroup();
    } else {
      setLoading(false);
    }
  }, [groupName]);

  if (loading) return null;

  if (groupName !== "xiangma") {
    return (
      <div className="card border-0 shadow-sm">
        <div className="card-body p-4">
          <h2 className="h4 mb-2">{groupInfo?.display_name || groupName}</h2>
          <p className="text-body-secondary mb-0">
            {groupInfo?.desc || "社群信息加载中..."}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="d-flex flex-column gap-4">
      {/* Group header */}
      <div className="card border-0 shadow-sm">
        <div className="card-body p-4">
          <h2 className="h3 mb-2">响马读paper</h2>
          <p className="text-body-secondary lead mb-0">
            一个学术交流社群，鼓励成员每月至少读一篇文献并打卡分享。我们相信在学术道路上，坚持阅读和分享是不断进步的关键。
          </p>
        </div>
      </div>

      {/* Community rules */}
      <div className="card border-0 shadow-sm">
        <div className="card-body p-4">
          <h3 className="h5 mb-3">社群规则</h3>
          <div className="d-flex flex-column gap-2">
            {RULES.map((rule) => (
              <div key={rule.title} className="card">
                <div className="card-header py-2 fw-semibold">
                  {rule.title}
                </div>
                <div className="card-body py-3">
                  <ul className="mb-0">
                    {rule.items.map((item, i) => (
                      <li key={i} className="mb-1">
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Sharing sessions */}
      <div className="card border-0 shadow-sm">
        <div className="card-body p-4">
          <h3 className="h5 mb-1">线上分享活动</h3>
          <p className="text-body-secondary small mb-3">
            社群已举办过多次线上分享活动，除特殊情况外，均有录屏视频供回放。
          </p>
          <ul className="list-group list-group-flush">
            {SESSIONS.map((s, idx) => (
              <li
                key={idx}
                className="list-group-item d-flex flex-column flex-sm-row align-items-sm-center gap-2 px-0"
              >
                <span className="badge bg-body-tertiary text-body border flex-shrink-0">
                  {s.date}
                </span>
                <span>
                  {s.url ? (
                    <a
                      className="external-link"
                      href={s.url}
                      target="_blank"
                      rel="noreferrer"
                    >
                      {s.title}
                    </a>
                  ) : (
                    s.title
                  )}
                  {s.note && (
                    <span className="text-success small d-block">
                      （注：{s.note}）
                    </span>
                  )}
                </span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Join us */}
      <div className="card border-0 shadow-sm">
        <div className="card-body p-4">
          <h3 className="h5 mb-2">加入我们</h3>
          <div className="row align-items-center g-4">
            <div className="col-md-8">
              <p className="mb-2">
                愿意参加并坚持每月打卡（读至少一篇paper并分享）的，请加群主个人微信，并注明"加入响马读paper群"。
              </p>
              <p className="text-body-secondary small mb-0">
                我们希望创建一个有序、高效的学术交流平台，让每一位成员在这里都能有所收获，不断提升学术水平。欢迎新老朋友的加入，共同推动学术进步！
              </p>
            </div>
            <div className="col-md-4 text-center">
              <img
                className="img-fluid rounded border"
                src="/static/images/wechat-qrcode.png"
                width="140"
                height="140"
                alt="微信群二维码"
              />
              <div className="text-body-secondary small mt-2">微信群二维码</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Home;
