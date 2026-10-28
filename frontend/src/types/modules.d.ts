declare module "lucide-react" {
  import * as React from "react";

  export interface LucideProps extends React.SVGProps<SVGSVGElement> {
    size?: string | number;
    color?: string;
    strokeWidth?: string | number;
    className?: string;
  }

  export type LucideIcon = React.ForwardRefExoticComponent<
    React.PropsWithoutRef<LucideProps> & React.RefAttributes<SVGSVGElement>
  >;

  export const Sparkles: LucideIcon;
  export const Copy: LucideIcon;
  export const Check: LucideIcon;
  export const Download: LucideIcon;
  export const Terminal: LucideIcon;
  export const ShieldCheck: LucideIcon;
  export const Cpu: LucideIcon;
  export const Layers: LucideIcon;
  export const Gauge: LucideIcon;
  export const Sliders: LucideIcon;
  export const ChevronDown: LucideIcon;
  export const ChevronUp: LucideIcon;
  export const RotateCcw: LucideIcon;
  export const AlertCircle: LucideIcon;
  export const FileText: LucideIcon;
  export const Zap: LucideIcon;
  export const CheckCircle2: LucideIcon;
  export const HelpCircle: LucideIcon;
  export const ExternalLink: LucideIcon;
  export const BookOpen: LucideIcon;
  export const History: LucideIcon;
  export const Columns: LucideIcon;
  export const Clock: LucideIcon;
  export const Binary: LucideIcon;
  export const Bot: LucideIcon;
  export const X: LucideIcon;
  export const Trash2: LucideIcon;
  export const ThumbsUp: LucideIcon;
  export const ThumbsDown: LucideIcon;
  export const MessageSquarePlus: LucideIcon;
  export const Lightbulb: LucideIcon;

  const icons: { [key: string]: LucideIcon };
  export default icons;
}
