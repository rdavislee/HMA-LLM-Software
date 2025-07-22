import svgPaths from "./svg-y6v79f9pg5";
// import imgElement from "figma:asset/74e099670d9b6a3ab6f879ce0cefcb0cba5cab80.png";
const imgElement = "";
import { imgColor, imgElement1, imgElement2 } from "./svg-twcee";

function Avatar01() {
  return (
    <div
      className="absolute bg-[#f6faff] left-0 overflow-clip rounded-[100px] size-8 top-0"
      data-name="Avatar/01"
    >
      <div
        className="absolute bg-center bg-cover bg-no-repeat inset-0"
        data-name="Element"
        style={{ backgroundImage: `url('${imgElement}')` }}
      />
    </div>
  );
}

function CircleAvatar() {
  return (
    <div
      className="overflow-clip relative rounded-[200px] shrink-0 size-8"
      data-name="Circle Avatar"
    >
      <Avatar01 />
      <div className="absolute inset-0 pointer-events-none shadow-[0px_-2px_4px_0px_inset_rgba(35,136,255,0.08)]" />
    </div>
  );
}

function AccountName() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-0.5 items-center justify-start p-0 relative shrink-0"
      data-name="Account Name"
    >
      <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#19213d] text-[14px] text-left text-nowrap">
        <p className="block leading-[1.3] whitespace-pre">Mauro Sicard</p>
      </div>
    </div>
  );
}

function AccountWrapper() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-2 items-center justify-start p-0 relative shrink-0"
      data-name="Account Wrapper"
    >
      <CircleAvatar />
      <AccountName />
    </div>
  );
}

function LineRoundedSettings() {
  return (
    <div className="relative shrink-0 size-4" data-name="Line Rounded/Settings">
      <div className="absolute bottom-[-0.422%] left-0 right-0 top-[-0.422%]">
        <svg
          className="block size-full"
          fill="none"
          preserveAspectRatio="none"
          viewBox="0 0 16 18"
        >
          <g id="Line Rounded/Settings">
            <path
              d={svgPaths.p2faf7900}
              id="Element"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeWidth="1.3"
            />
          </g>
        </svg>
      </div>
    </div>
  );
}

function LineRoundedSidebarLeft() {
  return (
    <div
      className="relative shrink-0 size-4"
      data-name="Line Rounded/Sidebar Left"
    >
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 16 16"
      >
        <g id="Line Rounded/Sidebar Left">
          <path
            d={svgPaths.pb0e5f00}
            id="Element"
            stroke="var(--stroke-0, #666F8D)"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="1.3"
          />
        </g>
      </svg>
    </div>
  );
}

function ActionIcons() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-3 items-center justify-end p-0 relative shrink-0"
      data-name="Action Icons"
    >
      <LineRoundedSettings />
      <LineRoundedSidebarLeft />
    </div>
  );
}

function AvatarAndIcons() {
  return (
    <div
      className="box-border content-stretch flex flex-row items-center justify-between p-0 relative shrink-0 w-full"
      data-name="Avatar And Icons"
    >
      <AccountWrapper />
      <ActionIcons />
    </div>
  );
}

function LineRoundedSearch() {
  return (
    <div
      className="relative shrink-0 size-[13px]"
      data-name="Line Rounded/Search"
    >
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 13 13"
      >
        <g id="Line Rounded/Search">
          <path
            d={svgPaths.pb70fc00}
            id="Element"
            stroke="var(--stroke-0, #666F8D)"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="1.2"
          />
        </g>
      </svg>
    </div>
  );
}

function PlaceholderWrapper() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-1 items-center justify-start p-0 relative shrink-0"
      data-name="Placeholder Wrapper"
    >
      <LineRoundedSearch />
      <div className="font-['Inter:Regular',_sans-serif] font-normal leading-[0] not-italic relative shrink-0 text-[#666f8d] text-[12px] text-left text-nowrap">
        <p className="block leading-[1.3] whitespace-pre">
          Search for conversations...
        </p>
      </div>
    </div>
  );
}

function Element() {
  return (
    <div
      className="absolute bottom-[7.5%] left-[7.5%] right-[7.5%] top-[7.5%]"
      data-name="Element"
    >
      <div className="absolute bottom-[-6.417%] left-[-6.417%] right-[-6.417%] top-[-6.417%]">
        <svg
          className="block size-full"
          fill="none"
          preserveAspectRatio="none"
          viewBox="0 0 11 11"
        >
          <g id="Element">
            <path
              d={svgPaths.p3a35fe80}
              id="Element_2"
              stroke="var(--stroke-0, #19213D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.2"
            />
          </g>
        </svg>
      </div>
    </div>
  );
}

function LineRoundedCommand() {
  return (
    <div
      className="relative shrink-0 size-[11px]"
      data-name="Line Rounded/Command"
    >
      <Element />
    </div>
  );
}

function Badge() {
  return (
    <div
      className="bg-[#f7f8fa] box-border content-stretch flex flex-row gap-1 items-center justify-center p-[6px] relative rounded shadow-[0px_1px_3px_0px_rgba(25,33,61,0.1)] shrink-0"
      data-name="Badge"
    >
      <LineRoundedCommand />
      <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#19213d] text-[12px] text-center text-nowrap">
        <p className="block leading-[1.3] whitespace-pre">C</p>
      </div>
    </div>
  );
}

function InputText() {
  return (
    <div
      className="bg-[#ffffff] h-[42px] min-h-[39px] relative rounded-lg shrink-0 w-full"
      data-name="Input Text"
    >
      <div className="absolute border border-[#f0f2f5] border-solid inset-0 pointer-events-none rounded-lg shadow-[0px_1px_3px_0px_rgba(25,33,61,0.1)]" />
      <div className="flex flex-row items-center min-h-inherit relative size-full">
        <div className="box-border content-stretch flex flex-row h-[42px] items-center justify-between min-h-inherit pl-3 pr-1.5 py-1.5 relative w-full">
          <PlaceholderWrapper />
          <Badge />
        </div>
      </div>
    </div>
  );
}

function SidebarTop() {
  return (
    <div
      className="box-border content-stretch flex flex-col gap-3 items-start justify-start p-0 relative shrink-0 w-full"
      data-name="Sidebar Top"
    >
      <AvatarAndIcons />
      <InputText />
    </div>
  );
}

function LineRoundedMessage() {
  return (
    <div className="relative shrink-0 size-4" data-name="Line Rounded/Message">
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 16 16"
      >
        <g id="Line Rounded/Message">
          <path
            d={svgPaths.p1a551e00}
            id="Element"
            stroke="var(--stroke-0, #19213D)"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="0.96"
          />
          <path
            d={svgPaths.p163be380}
            id="Element_2"
            stroke="var(--stroke-0, #19213D)"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="0.96"
          />
          <path
            d={svgPaths.p32d14e60}
            id="Element_3"
            stroke="var(--stroke-0, #19213D)"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="0.96"
          />
          <g id="Element_4">
            <path
              d={svgPaths.p18315b40}
              id="Element_5"
              stroke="var(--stroke-0, #19213D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.p8bcfc80}
              id="Element_6"
              stroke="var(--stroke-0, #19213D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.pe6cfb60}
              id="Element_7"
              stroke="var(--stroke-0, #19213D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.p4c94480}
              id="Element_8"
              stroke="var(--stroke-0, #19213D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.4"
            />
          </g>
        </g>
      </svg>
    </div>
  );
}

function TextWrapper() {
  return (
    <div
      className="basis-0 box-border content-stretch flex flex-row gap-2 grow items-center justify-start min-h-px min-w-px p-0 relative shrink-0"
      data-name="Text Wrapper"
    >
      <LineRoundedMessage />
      <div className="basis-0 font-['Inter:Regular',_sans-serif] font-normal grow leading-[0] min-h-px min-w-px not-italic relative shrink-0 text-[#19213d] text-[14px] text-left">
        <p className="block leading-[1.3]">Conversations</p>
      </div>
    </div>
  );
}

function Element2() {
  return (
    <div
      className="absolute bottom-[7.5%] left-[7.5%] right-[7.5%] top-[7.5%]"
      data-name="Element"
    >
      <div className="absolute bottom-[-6.417%] left-[-6.417%] right-[-6.417%] top-[-6.417%]">
        <svg
          className="block size-full"
          fill="none"
          preserveAspectRatio="none"
          viewBox="0 0 11 11"
        >
          <g id="Element">
            <path
              d={svgPaths.p3a35fe80}
              id="Element_2"
              stroke="var(--stroke-0, #19213D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.2"
            />
          </g>
        </svg>
      </div>
    </div>
  );
}

function LineRoundedCommand1() {
  return (
    <div
      className="relative shrink-0 size-[11px]"
      data-name="Line Rounded/Command"
    >
      <Element2 />
    </div>
  );
}

function Badge2() {
  return (
    <div
      className="bg-[#f7f8fa] box-border content-stretch flex flex-row gap-1 items-center justify-center p-[6px] relative rounded shadow-[0px_1px_3px_0px_rgba(25,33,61,0.1)] shrink-0 w-9"
      data-name="Badge"
    >
      <LineRoundedCommand1 />
      <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#19213d] text-[12px] text-center text-nowrap">
        <p className="block leading-[1.3] whitespace-pre">5</p>
      </div>
    </div>
  );
}

function SidebarLinkItem() {
  return (
    <div
      className="bg-[#353e5c] h-[43px] relative rounded-lg shadow-[0px_1px_3px_0px_rgba(25,33,61,0.1)] shrink-0 w-full"
      data-name="Sidebar Link Item"
    >
      <div className="flex flex-row items-center overflow-clip relative size-full">
        <div className="box-border content-stretch flex flex-row h-[43px] items-center justify-between pl-3 pr-2.5 py-2 relative w-full">
          <TextWrapper />
          <Badge2 />
        </div>
      </div>
    </div>
  );
}

function LineRoundedBook() {
  return (
    <div className="relative shrink-0 size-4" data-name="Line Rounded/Book">
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 16 16"
      >
        <g id="Line Rounded/Book">
          <path
            d={svgPaths.p31605d80}
            id="Element"
            stroke="var(--stroke-0, #666F8D)"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="1.12"
          />
        </g>
      </svg>
    </div>
  );
}

function TextWrapper1() {
  return (
    <div
      className="basis-0 box-border content-stretch flex flex-row gap-2 grow items-center justify-start min-h-px min-w-px p-0 relative shrink-0"
      data-name="Text Wrapper"
    >
      <LineRoundedBook />
      <div className="basis-0 font-['Inter:Regular',_sans-serif] font-normal grow leading-[0] min-h-px min-w-px not-italic overflow-ellipsis overflow-hidden relative shrink-0 text-[#666f8d] text-[14px] text-left text-nowrap">
        <p className="[text-overflow:inherit] [text-wrap-mode:inherit]\' [white-space-collapse:inherit] block leading-[1.3] overflow-inherit">
          Resource Center
        </p>
      </div>
    </div>
  );
}

function Element3() {
  return (
    <div
      className="absolute bottom-[7.5%] left-[7.5%] right-[7.5%] top-[7.5%]"
      data-name="Element"
    >
      <div className="absolute bottom-[-6.417%] left-[-6.417%] right-[-6.417%] top-[-6.417%]">
        <svg
          className="block size-full"
          fill="none"
          preserveAspectRatio="none"
          viewBox="0 0 11 11"
        >
          <g id="Element">
            <path
              d={svgPaths.p3a35fe80}
              id="Element_2"
              stroke="var(--stroke-0, #19213D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.2"
            />
          </g>
        </svg>
      </div>
    </div>
  );
}

function LineRoundedCommand2() {
  return (
    <div
      className="relative shrink-0 size-[11px]"
      data-name="Line Rounded/Command"
    >
      <Element3 />
    </div>
  );
}

function Badge3() {
  return (
    <div
      className="bg-[#f7f8fa] box-border content-stretch flex flex-row gap-1 items-center justify-center p-[6px] relative rounded shadow-[0px_1px_3px_0px_rgba(25,33,61,0.1)] shrink-0 w-9"
      data-name="Badge"
    >
      <LineRoundedCommand2 />
      <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#19213d] text-[12px] text-center text-nowrap">
        <p className="block leading-[1.3] whitespace-pre">4</p>
      </div>
    </div>
  );
}

function SidebarLinkItem1() {
  return (
    <div
      className="h-[43px] relative rounded-lg shrink-0 w-full"
      data-name="Sidebar Link Item"
    >
      <div className="flex flex-row items-center overflow-clip relative size-full">
        <div className="box-border content-stretch flex flex-row h-[43px] items-center justify-between pl-3 pr-2.5 py-2 relative w-full">
          <TextWrapper1 />
          <Badge3 />
        </div>
      </div>
    </div>
  );
}

function Element4() {
  return (
    <div
      className="absolute bottom-[5.472%] left-[5.422%] right-[5.422%] top-[5.472%]"
      data-name="Element"
    >
      <div className="absolute bottom-[-3.93%] left-[-3.926%] right-[-3.925%] top-[-3.93%]">
        <svg
          className="block size-full"
          fill="none"
          preserveAspectRatio="none"
          viewBox="0 0 16 16"
        >
          <g id="Element">
            <g id="Element_2">
              <path
                d={svgPaths.p7ec3d00}
                stroke="var(--stroke-0, #666F8D)"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="1.12"
              />
              <path
                d={svgPaths.p1fd79500}
                stroke="var(--stroke-0, #666F8D)"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="1.12"
              />
              <path
                d={svgPaths.p3d3c7b00}
                stroke="var(--stroke-0, #666F8D)"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="1.12"
              />
              <path
                d={svgPaths.p28681100}
                stroke="var(--stroke-0, #666F8D)"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="1.12"
              />
            </g>
          </g>
        </svg>
      </div>
    </div>
  );
}

function LineRoundedGrid() {
  return (
    <div className="relative shrink-0 size-4" data-name="Line Rounded/Grid">
      <Element4 />
    </div>
  );
}

function TextWrapper2() {
  return (
    <div
      className="basis-0 box-border content-stretch flex flex-row gap-2 grow items-center justify-start min-h-px min-w-px p-0 relative shrink-0"
      data-name="Text Wrapper"
    >
      <LineRoundedGrid />
      <div className="basis-0 font-['Inter:Regular',_sans-serif] font-normal grow leading-[0] min-h-px min-w-px not-italic overflow-ellipsis overflow-hidden relative shrink-0 text-[#666f8d] text-[14px] text-left text-nowrap">
        <p className="[text-overflow:inherit] [text-wrap-mode:inherit]\' [white-space-collapse:inherit] block leading-[1.3] overflow-inherit">
          Utilities
        </p>
      </div>
    </div>
  );
}

function Element5() {
  return (
    <div
      className="absolute bottom-[7.5%] left-[7.5%] right-[7.5%] top-[7.5%]"
      data-name="Element"
    >
      <div className="absolute bottom-[-6.417%] left-[-6.417%] right-[-6.417%] top-[-6.417%]">
        <svg
          className="block size-full"
          fill="none"
          preserveAspectRatio="none"
          viewBox="0 0 11 11"
        >
          <g id="Element">
            <path
              d={svgPaths.p34623780}
              id="Element_2"
              stroke="var(--stroke-0, #19213D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.2"
            />
          </g>
        </svg>
      </div>
    </div>
  );
}

function LineRoundedCommand3() {
  return (
    <div
      className="relative shrink-0 size-[11px]"
      data-name="Line Rounded/Command"
    >
      <Element5 />
    </div>
  );
}

function Badge4() {
  return (
    <div
      className="bg-[#f7f8fa] box-border content-stretch flex flex-row gap-1 items-center justify-center p-[6px] relative rounded shadow-[0px_1px_3px_0px_rgba(25,33,61,0.1)] shrink-0 w-9"
      data-name="Badge"
    >
      <LineRoundedCommand3 />
      <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#19213d] text-[12px] text-center text-nowrap">
        <p className="block leading-[1.3] whitespace-pre">7</p>
      </div>
    </div>
  );
}

function SidebarLinkItem2() {
  return (
    <div
      className="h-[43px] relative rounded-lg shrink-0 w-full"
      data-name="Sidebar Link Item"
    >
      <div className="flex flex-row items-center overflow-clip relative size-full">
        <div className="box-border content-stretch flex flex-row h-[43px] items-center justify-between pl-3 pr-2.5 py-2 relative w-full">
          <TextWrapper2 />
          <Badge4 />
        </div>
      </div>
    </div>
  );
}

function LinksList() {
  return (
    <div
      className="box-border content-stretch flex flex-col gap-0.5 items-start justify-start p-0 relative shrink-0 w-full"
      data-name="Links List"
    >
      <SidebarLinkItem />
      <SidebarLinkItem1 />
      <SidebarLinkItem2 />
    </div>
  );
}

function SidebarLinksListWrapper() {
  return (
    <div
      className="box-border content-stretch flex flex-col gap-3 items-start justify-start p-0 relative shrink-0 w-full"
      data-name="Sidebar Links List Wrapper"
    >
      <LinksList />
    </div>
  );
}

function SidebarListTitleWrapper1() {
  return (
    <div
      className="relative shrink-0 w-full"
      data-name="Sidebar List Title Wrapper"
    >
      <div className="flex flex-row items-center relative size-full">
        <div className="box-border content-stretch flex flex-row items-center justify-start px-2.5 py-0 relative w-full">
          <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#bac0cc] text-[12px] text-left text-nowrap tracking-[1.2px] uppercase">
            <p className="adjustLetterSpacing block leading-[1.3] whitespace-pre">
              Starred
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function TextWrapper3() {
  return (
    <div
      className="basis-0 box-border content-stretch flex flex-row gap-2 grow items-center justify-start min-h-px min-w-px p-0 relative shrink-0"
      data-name="Text Wrapper"
    >
      <div className="basis-0 font-['Inter:Regular',_sans-serif] font-normal grow leading-[0] min-h-px min-w-px not-italic overflow-ellipsis overflow-hidden relative shrink-0 text-[#666f8d] text-[14px] text-left text-nowrap">
        <p className="[text-overflow:inherit] [text-wrap-mode:inherit]\' [white-space-collapse:inherit] block leading-[1.3] overflow-inherit">
          This is a placeholder for useful information.
        </p>
      </div>
    </div>
  );
}

function SidebarLinkItem3() {
  return (
    <div
      className="h-[43px] relative rounded-lg shrink-0 w-full"
      data-name="Sidebar Link Item"
    >
      <div className="flex flex-row items-center overflow-clip relative size-full">
        <div className="box-border content-stretch flex flex-row h-[43px] items-center justify-start pl-3 pr-2.5 py-2 relative w-full">
          <TextWrapper3 />
        </div>
      </div>
    </div>
  );
}

function TextWrapper4() {
  return (
    <div
      className="basis-0 box-border content-stretch flex flex-row gap-2 grow items-center justify-start min-h-px min-w-px p-0 relative shrink-0"
      data-name="Text Wrapper"
    >
      <div className="basis-0 font-['Inter:Regular',_sans-serif] font-normal grow leading-[0] min-h-px min-w-px not-italic overflow-ellipsis overflow-hidden relative shrink-0 text-[#666f8d] text-[14px] text-left text-nowrap">
        <p className="[text-overflow:inherit] [text-wrap-mode:inherit]\' [white-space-collapse:inherit] block leading-[1.3] overflow-inherit">
          An error occurred while processing your request.
        </p>
      </div>
    </div>
  );
}

function SidebarLinkItem4() {
  return (
    <div
      className="h-[43px] relative rounded-lg shrink-0 w-full"
      data-name="Sidebar Link Item"
    >
      <div className="flex flex-row items-center overflow-clip relative size-full">
        <div className="box-border content-stretch flex flex-row h-[43px] items-center justify-start pl-3 pr-2.5 py-2 relative w-full">
          <TextWrapper4 />
        </div>
      </div>
    </div>
  );
}

function TextWrapper5() {
  return (
    <div
      className="basis-0 box-border content-stretch flex flex-row gap-2 grow items-center justify-start min-h-px min-w-px p-0 relative shrink-0"
      data-name="Text Wrapper"
    >
      <div className="basis-0 font-['Inter:Regular',_sans-serif] font-normal grow leading-[0] min-h-px min-w-px not-italic overflow-ellipsis overflow-hidden relative shrink-0 text-[#666f8d] text-[14px] text-left text-nowrap">
        <p className="[text-overflow:inherit] [text-wrap-mode:inherit]\' [white-space-collapse:inherit] block leading-[1.3] overflow-inherit">
          Please ensure all fields are filled out correctly.
        </p>
      </div>
    </div>
  );
}

function SidebarLinkItem5() {
  return (
    <div
      className="h-[43px] relative rounded-lg shrink-0 w-full"
      data-name="Sidebar Link Item"
    >
      <div className="flex flex-row items-center overflow-clip relative size-full">
        <div className="box-border content-stretch flex flex-row h-[43px] items-center justify-start pl-3 pr-2.5 py-2 relative w-full">
          <TextWrapper5 />
        </div>
      </div>
    </div>
  );
}

function TextWrapper6() {
  return (
    <div
      className="basis-0 box-border content-stretch flex flex-row gap-2 grow items-center justify-start min-h-px min-w-px p-0 relative shrink-0"
      data-name="Text Wrapper"
    >
      <div className="basis-0 font-['Inter:Regular',_sans-serif] font-normal grow leading-[0] min-h-px min-w-px not-italic overflow-ellipsis overflow-hidden relative shrink-0 text-[#666f8d] text-[14px] text-left text-nowrap">
        <p className="[text-overflow:inherit] [text-wrap-mode:inherit]\' [white-space-collapse:inherit] block leading-[1.3] overflow-inherit">
          The project deadline is approaching quickly.
        </p>
      </div>
    </div>
  );
}

function SidebarLinkItem6() {
  return (
    <div
      className="h-[43px] relative rounded-lg shrink-0 w-full"
      data-name="Sidebar Link Item"
    >
      <div className="flex flex-row items-center overflow-clip relative size-full">
        <div className="box-border content-stretch flex flex-row h-[43px] items-center justify-start pl-3 pr-2.5 py-2 relative w-full">
          <TextWrapper6 />
        </div>
      </div>
    </div>
  );
}

function LinksList1() {
  return (
    <div
      className="box-border content-stretch flex flex-col gap-0.5 items-start justify-start p-0 relative shrink-0 w-full"
      data-name="Links List"
    >
      <SidebarLinkItem3 />
      <SidebarLinkItem4 />
      <SidebarLinkItem5 />
      <SidebarLinkItem6 />
    </div>
  );
}

function SidebarLinksListWrapper1() {
  return (
    <div
      className="box-border content-stretch flex flex-col gap-3 items-start justify-start p-0 relative shrink-0 w-full"
      data-name="Sidebar Links List Wrapper"
    >
      <SidebarListTitleWrapper1 />
      <LinksList1 />
    </div>
  );
}

function SidebarListTitleWrapper2() {
  return (
    <div
      className="relative shrink-0 w-full"
      data-name="Sidebar List Title Wrapper"
    >
      <div className="flex flex-row items-center relative size-full">
        <div className="box-border content-stretch flex flex-row items-center justify-start px-2.5 py-0 relative w-full">
          <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#bac0cc] text-[12px] text-left text-nowrap tracking-[1.2px] uppercase">
            <p className="adjustLetterSpacing block leading-[1.3] whitespace-pre">
              Conversation Log
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function TextWrapper7() {
  return (
    <div
      className="basis-0 box-border content-stretch flex flex-row gap-2 grow items-center justify-start min-h-px min-w-px p-0 relative shrink-0"
      data-name="Text Wrapper"
    >
      <div className="basis-0 font-['Inter:Regular',_sans-serif] font-normal grow leading-[0] min-h-px min-w-px not-italic overflow-ellipsis overflow-hidden relative shrink-0 text-[#666f8d] text-[14px] text-left text-nowrap">
        <p className="[text-overflow:inherit] [text-wrap-mode:inherit]\' [white-space-collapse:inherit] block leading-[1.3] overflow-inherit">
          Please hold while I fetch the details.
        </p>
      </div>
    </div>
  );
}

function SidebarLinkItem7() {
  return (
    <div
      className="h-[43px] relative rounded-lg shrink-0 w-full"
      data-name="Sidebar Link Item"
    >
      <div className="flex flex-row items-center overflow-clip relative size-full">
        <div className="box-border content-stretch flex flex-row h-[43px] items-center justify-start pl-3 pr-2.5 py-2 relative w-full">
          <TextWrapper7 />
        </div>
      </div>
    </div>
  );
}

function TextWrapper8() {
  return (
    <div
      className="basis-0 box-border content-stretch flex flex-row gap-2 grow items-center justify-start min-h-px min-w-px p-0 relative shrink-0"
      data-name="Text Wrapper"
    >
      <div className="basis-0 font-['Inter:Regular',_sans-serif] font-normal grow leading-[0] min-h-px min-w-px not-italic overflow-ellipsis overflow-hidden relative shrink-0 text-[#666f8d] text-[14px] text-left text-nowrap">
        <p className="[text-overflow:inherit] [text-wrap-mode:inherit]\' [white-space-collapse:inherit] block leading-[1.3] overflow-inherit">{`Let's get started with your request.`}</p>
      </div>
    </div>
  );
}

function SidebarLinkItem8() {
  return (
    <div
      className="h-[43px] relative rounded-lg shrink-0 w-full"
      data-name="Sidebar Link Item"
    >
      <div className="flex flex-row items-center overflow-clip relative size-full">
        <div className="box-border content-stretch flex flex-row h-[43px] items-center justify-start pl-3 pr-2.5 py-2 relative w-full">
          <TextWrapper8 />
        </div>
      </div>
    </div>
  );
}

function TextWrapper9() {
  return (
    <div
      className="basis-0 box-border content-stretch flex flex-row gap-2 grow items-center justify-start min-h-px min-w-px p-0 relative shrink-0"
      data-name="Text Wrapper"
    >
      <div className="basis-0 font-['Inter:Regular',_sans-serif] font-normal grow leading-[0] min-h-px min-w-px not-italic overflow-ellipsis overflow-hidden relative shrink-0 text-[#666f8d] text-[14px] text-left text-nowrap">
        <p className="[text-overflow:inherit] [text-wrap-mode:inherit]\' [white-space-collapse:inherit] block leading-[1.3] overflow-inherit">
          The system is currently processing your input.
        </p>
      </div>
    </div>
  );
}

function SidebarLinkItem9() {
  return (
    <div
      className="h-[43px] relative rounded-lg shrink-0 w-full"
      data-name="Sidebar Link Item"
    >
      <div className="flex flex-row items-center overflow-clip relative size-full">
        <div className="box-border content-stretch flex flex-row h-[43px] items-center justify-start pl-3 pr-2.5 py-2 relative w-full">
          <TextWrapper9 />
        </div>
      </div>
    </div>
  );
}

function TextWrapper10() {
  return (
    <div
      className="basis-0 box-border content-stretch flex flex-row gap-2 grow items-center justify-start min-h-px min-w-px p-0 relative shrink-0"
      data-name="Text Wrapper"
    >
      <div className="basis-0 font-['Inter:Regular',_sans-serif] font-normal grow leading-[0] min-h-px min-w-px not-italic overflow-ellipsis overflow-hidden relative shrink-0 text-[#666f8d] text-[14px] text-left text-nowrap">
        <p className="[text-overflow:inherit] [text-wrap-mode:inherit]\' [white-space-collapse:inherit] block leading-[1.3] overflow-inherit">
          This section contains important updates.
        </p>
      </div>
    </div>
  );
}

function SidebarLinkItem10() {
  return (
    <div
      className="h-[43px] relative rounded-lg shrink-0 w-full"
      data-name="Sidebar Link Item"
    >
      <div className="flex flex-row items-center overflow-clip relative size-full">
        <div className="box-border content-stretch flex flex-row h-[43px] items-center justify-start pl-3 pr-2.5 py-2 relative w-full">
          <TextWrapper10 />
        </div>
      </div>
    </div>
  );
}

function TextWrapper11() {
  return (
    <div
      className="basis-0 box-border content-stretch flex flex-row gap-2 grow items-center justify-start min-h-px min-w-px p-0 relative shrink-0"
      data-name="Text Wrapper"
    >
      <div className="basis-0 font-['Inter:Regular',_sans-serif] font-normal grow leading-[0] min-h-px min-w-px not-italic overflow-ellipsis overflow-hidden relative shrink-0 text-[#666f8d] text-[14px] text-left text-nowrap">
        <p className="[text-overflow:inherit] [text-wrap-mode:inherit]\' [white-space-collapse:inherit] block leading-[1.3] overflow-inherit">
          Please check your internet connection.
        </p>
      </div>
    </div>
  );
}

function SidebarLinkItem11() {
  return (
    <div
      className="h-[43px] relative rounded-lg shrink-0 w-full"
      data-name="Sidebar Link Item"
    >
      <div className="flex flex-row items-center overflow-clip relative size-full">
        <div className="box-border content-stretch flex flex-row h-[43px] items-center justify-start pl-3 pr-2.5 py-2 relative w-full">
          <TextWrapper11 />
        </div>
      </div>
    </div>
  );
}

function TextWrapper12() {
  return (
    <div
      className="basis-0 box-border content-stretch flex flex-row gap-2 grow items-center justify-start min-h-px min-w-px p-0 relative shrink-0"
      data-name="Text Wrapper"
    >
      <div className="basis-0 font-['Inter:Regular',_sans-serif] font-normal grow leading-[0] min-h-px min-w-px not-italic overflow-ellipsis overflow-hidden relative shrink-0 text-[#666f8d] text-[14px] text-left text-nowrap">
        <p className="[text-overflow:inherit] [text-wrap-mode:inherit]\' [white-space-collapse:inherit] block leading-[1.3] overflow-inherit">
          Age is just a number.
        </p>
      </div>
    </div>
  );
}

function SidebarLinkItem12() {
  return (
    <div
      className="h-[43px] relative rounded-lg shrink-0 w-full"
      data-name="Sidebar Link Item"
    >
      <div className="flex flex-row items-center overflow-clip relative size-full">
        <div className="box-border content-stretch flex flex-row h-[43px] items-center justify-start pl-3 pr-2.5 py-2 relative w-full">
          <TextWrapper12 />
        </div>
      </div>
    </div>
  );
}

function LinksList2() {
  return (
    <div
      className="box-border content-stretch flex flex-col gap-0.5 items-start justify-start p-0 relative shrink-0 w-full"
      data-name="Links List"
    >
      <SidebarLinkItem7 />
      <SidebarLinkItem8 />
      <SidebarLinkItem9 />
      <SidebarLinkItem10 />
      <SidebarLinkItem11 />
      <SidebarLinkItem12 />
    </div>
  );
}

function Gradient() {
  return (
    <div
      className="absolute bottom-[0.205px] contents left-[0.219px] right-[-0.219px] top-[178.896px]"
      data-name="Gradient"
    >
      <div
        className="absolute bg-[#f7f8fa] bottom-[0.205px] left-[0.219px] mask-alpha mask-intersect mask-no-clip mask-no-repeat mask-position-[0%] mask-size-[100%_100%] right-[-0.219px] top-[178.896px]"
        data-name="Color"
        style={{ maskImage: `url('${imgColor}')` }}
      />
    </div>
  );
}

function SidebarLinksListWrapper2() {
  return (
    <div
      className="box-border content-stretch flex flex-col gap-3 items-start justify-start p-0 relative shrink-0 w-full"
      data-name="Sidebar Links List Wrapper"
    >
      <SidebarListTitleWrapper2 />
      <LinksList2 />
      <Gradient />
    </div>
  );
}

function SidebarMainItemsWrapper() {
  return (
    <div
      className="box-border content-stretch flex flex-col gap-10 items-start justify-start p-0 relative shrink-0 w-full"
      data-name="Sidebar Main Items Wrapper"
    >
      <SidebarTop />
      <SidebarLinksListWrapper />
      <SidebarLinksListWrapper1 />
      <SidebarLinksListWrapper2 />
    </div>
  );
}

function LineRoundedPlus() {
  return (
    <div
      className="relative shrink-0 size-[15px]"
      data-name="Line Rounded/Plus"
    >
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 15 15"
      >
        <g id="Line Rounded/Plus">
          <path
            d={svgPaths.pf0bdd20}
            id="Element"
            stroke="var(--stroke-0, white)"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="1.125"
          />
        </g>
      </svg>
    </div>
  );
}

function PrimaryButton() {
  return (
    <div
      className="bg-gradient-to-b from-[#2b7afb] relative rounded-lg shrink-0 to-[#213bfd] via-100% via-[#2174fd] w-full"
      data-name="Primary Button"
    >
      <div className="absolute border border-[#174bd2] border-solid inset-0 pointer-events-none rounded-lg shadow-[0px_2px_5px_0px_rgba(20,88,201,0.17)]" />
      <div className="flex flex-row items-center justify-center relative size-full">
        <div className="box-border content-stretch flex flex-row gap-2 items-center justify-center px-4 py-3 relative w-full">
          <LineRoundedPlus />
          <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#ffffff] text-[14px] text-center text-nowrap">
            <p className="block leading-[1.3] whitespace-pre">
              Initiate a new conversation
            </p>
          </div>
        </div>
      </div>
      <div className="absolute inset-0 pointer-events-none shadow-[0px_-2px_0.3px_0px_inset_rgba(14,56,125,0.18),0px_2px_1px_0px_inset_rgba(255,255,255,0.22)]" />
    </div>
  );
}

function SidebarWrapper() {
  return (
    <div
      className="box-border content-stretch flex flex-col items-start justify-between min-w-[296px] overflow-clip pb-4 pt-6 px-6 relative self-stretch shrink-0 w-[296px]"
      data-name="Sidebar Wrapper"
    >
      <SidebarMainItemsWrapper />
      <PrimaryButton />
    </div>
  );
}

function TitleBadge() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-2 items-center justify-start p-0 relative shrink-0"
      data-name="Title & Badge"
    >
      <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#19213d] text-[16px] text-left text-nowrap">
        <p className="block leading-[1.3] whitespace-pre">Conversations</p>
      </div>
    </div>
  );
}

function LineRoundedSearch1() {
  return (
    <div
      className="relative shrink-0 size-[13px]"
      data-name="Line Rounded/Search"
    >
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 13 13"
      >
        <g id="Line Rounded/Search">
          <path
            d={svgPaths.pa92e80}
            id="Element"
            stroke="var(--stroke-0, #666F8D)"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="1.2"
          />
        </g>
      </svg>
    </div>
  );
}

function PlaceholderWrapper1() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-1 items-center justify-start p-0 relative shrink-0"
      data-name="Placeholder Wrapper"
    >
      <LineRoundedSearch1 />
      <div className="font-['Inter:Regular',_sans-serif] font-normal leading-[0] not-italic relative shrink-0 text-[#666f8d] text-[12px] text-left text-nowrap">
        <p className="block leading-[1.3] whitespace-pre">
          Search for conversations...
        </p>
      </div>
    </div>
  );
}

function Element16() {
  return (
    <div
      className="absolute bottom-[7.5%] left-[7.5%] right-[7.5%] top-[7.5%]"
      data-name="Element"
    >
      <div className="absolute bottom-[-6.417%] left-[-6.417%] right-[-6.417%] top-[-6.417%]">
        <svg
          className="block size-full"
          fill="none"
          preserveAspectRatio="none"
          viewBox="0 0 11 11"
        >
          <g id="Element">
            <path
              d={svgPaths.pcdef700}
              id="Element_2"
              stroke="var(--stroke-0, #19213D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.2"
            />
          </g>
        </svg>
      </div>
    </div>
  );
}

function LineRoundedCommand4() {
  return (
    <div
      className="relative shrink-0 size-[11px]"
      data-name="Line Rounded/Command"
    >
      <Element16 />
    </div>
  );
}

function Badge5() {
  return (
    <div
      className="bg-[#f7f8fa] box-border content-stretch flex flex-row gap-1 items-center justify-center p-[6px] relative rounded shadow-[0px_1px_3px_0px_rgba(25,33,61,0.1)] shrink-0"
      data-name="Badge"
    >
      <LineRoundedCommand4 />
      <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#19213d] text-[12px] text-center text-nowrap">
        <p className="block leading-[1.3] whitespace-pre">C</p>
      </div>
    </div>
  );
}

function InputText1() {
  return (
    <div
      className="bg-[#ffffff] box-border content-stretch flex flex-row h-full items-center justify-between min-h-[39px] pl-3 pr-1.5 py-1.5 relative rounded-lg shrink-0 w-[306px]"
      data-name="Input Text"
    >
      <div className="absolute border border-[#f0f2f5] border-solid inset-0 pointer-events-none rounded-lg shadow-[0px_1px_3px_0px_rgba(25,33,61,0.1)]" />
      <PlaceholderWrapper1 />
      <Badge5 />
    </div>
  );
}

function TopMenuLeft() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-6 items-center justify-start p-0 relative shrink-0"
      data-name="Top Menu Left"
    >
      <TitleBadge />
      <div className="flex flex-row items-center self-stretch">
        <InputText1 />
      </div>
    </div>
  );
}

function LineRoundedPlus1() {
  return (
    <div className="relative shrink-0 size-3" data-name="Line Rounded/Plus">
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 12 12"
      >
        <g id="Line Rounded/Plus">
          <path
            d="M6 1.5V10.5M10.5 6H1.5"
            id="Element"
            stroke="var(--stroke-0, white)"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="0.72"
          />
        </g>
      </svg>
    </div>
  );
}

function PrimaryButton1() {
  return (
    <div
      className="bg-gradient-to-b box-border content-stretch flex flex-row from-[#2b7afb] gap-1 items-center justify-center px-4 py-2 relative rounded-lg shrink-0 to-[#213bfd] via-100% via-[#2174fd]"
      data-name="Primary Button"
    >
      <div className="absolute border border-[#174bd2] border-solid inset-0 pointer-events-none rounded-lg shadow-[0px_2px_5px_0px_rgba(20,88,201,0.17)]" />
      <LineRoundedPlus1 />
      <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#ffffff] text-[12px] text-center text-nowrap">
        <p className="block leading-[1.3] whitespace-pre">
          Start a new conversation
        </p>
      </div>
      <div className="absolute inset-0 pointer-events-none shadow-[0px_-2px_0.3px_0px_inset_rgba(14,56,125,0.18),0px_2px_1px_0px_inset_rgba(255,255,255,0.22)]" />
    </div>
  );
}

function TopMenuRight() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-4 items-center justify-end p-0 relative shrink-0"
      data-name="Top Menu Right"
    >
      <PrimaryButton1 />
    </div>
  );
}

function TopBarWrapper() {
  return (
    <div
      className="bg-[#ffffff] relative shrink-0 w-full"
      data-name="Top Bar Wrapper"
    >
      <div className="flex flex-row items-center overflow-clip relative size-full">
        <div className="box-border content-stretch flex flex-row items-center justify-between px-6 py-4 relative w-full">
          <TopMenuLeft />
          <TopMenuRight />
        </div>
      </div>
      <div className="absolute border-[#e3e6ea] border-[0px_0px_1px] border-solid inset-0 pointer-events-none" />
    </div>
  );
}

function BackgroundChat() {
  return (
    <div
      className="absolute blur-[206.112px] filter left-[34.555px] opacity-[0.16] size-[1064.89px] top-[541.65px]"
      data-name="Background Chat"
    >
      <div
        className="absolute inset-0 mask-alpha mask-intersect mask-no-clip mask-no-repeat mask-position-[0px] mask-size-[1064.89px_1064.89px]"
        data-name="Element"
        style={{ maskImage: `url('${imgElement1}')` }}
      >
        <svg
          className="block size-full"
          fill="none"
          preserveAspectRatio="none"
          viewBox="0 0 1065 1065"
        >
          <circle
            cx="532.446"
            cy="532.446"
            fill="url(#paint0_radial_1_6607)"
            id="Element"
            r="532.446"
          />
          <defs>
            <radialGradient
              cx="0"
              cy="0"
              gradientTransform="translate(619.222 350.169) rotate(103.201) scale(608.625)"
              gradientUnits="userSpaceOnUse"
              id="paint0_radial_1_6607"
              r="1"
            >
              <stop stopColor="#0679FF" />
              <stop offset="1" stopColor="#2A8CFF" />
            </radialGradient>
          </defs>
        </svg>
      </div>
      <div
        className="absolute bottom-[48.276%] left-[-40.868%] mask-alpha mask-intersect mask-no-clip mask-no-repeat mask-position-[435.203px_416.824px] mask-size-[1064.89px_1064.89px] right-[50.002%] top-[-39.142%]"
        data-name="Element"
        style={{ maskImage: `url('${imgElement1}')` }}
      >
        <div className="absolute inset-[-32.098%]">
          <svg
            className="block size-full"
            fill="none"
            preserveAspectRatio="none"
            viewBox="0 0 1590 1590"
          >
            <g filter="url(#filter0_f_1_6586)" id="Element">
              <circle
                cx="794.814"
                cy="794.814"
                fill="var(--fill-0, #5344FE)"
                fillOpacity="0.68"
                r="483.814"
              />
            </g>
            <defs>
              <filter
                colorInterpolationFilters="sRGB"
                filterUnits="userSpaceOnUse"
                height="1588.82"
                id="filter0_f_1_6586"
                width="1588.82"
                x="0.406433"
                y="0.406433"
              >
                <feFlood floodOpacity="0" result="BackgroundImageFix" />
                <feBlend
                  in="SourceGraphic"
                  in2="BackgroundImageFix"
                  mode="normal"
                  result="shape"
                />
                <feGaussianBlur
                  result="effect1_foregroundBlur_1_6586"
                  stdDeviation="155.297"
                />
              </filter>
            </defs>
          </svg>
        </div>
      </div>
      <div
        className="absolute bottom-[17.105%] left-[77.849%] mask-alpha mask-intersect mask-no-clip mask-no-repeat mask-position-[-829.008px_-182.15px] mask-size-[1064.89px_1064.89px] mix-blend-overlay right-[-43.639%] top-[17.105%]"
        data-name="Element"
        style={{ maskImage: `url('${imgElement1}')` }}
      >
        <div className="absolute inset-[-53.833%]">
          <svg
            className="block size-full"
            fill="none"
            preserveAspectRatio="none"
            viewBox="0 0 1456 1456"
          >
            <g
              filter="url(#filter0_f_1_6617)"
              id="Element"
              style={{ mixBlendMode: "overlay" }}
            >
              <circle
                cx="728.294"
                cy="728.294"
                fill="var(--fill-0, #FE445A)"
                r="350.294"
              />
            </g>
            <defs>
              <filter
                colorInterpolationFilters="sRGB"
                filterUnits="userSpaceOnUse"
                height="1454.89"
                id="filter0_f_1_6617"
                width="1454.89"
                x="0.850647"
                y="0.850647"
              >
                <feFlood floodOpacity="0" result="BackgroundImageFix" />
                <feBlend
                  in="SourceGraphic"
                  in2="BackgroundImageFix"
                  mode="normal"
                  result="shape"
                />
                <feGaussianBlur
                  result="effect1_foregroundBlur_1_6617"
                  stdDeviation="188.575"
                />
              </filter>
            </defs>
          </svg>
        </div>
      </div>
      <div
        className="absolute bottom-[11.072%] left-[-19.352%] mask-alpha mask-intersect mask-no-clip mask-no-repeat mask-position-[206.078px_-246.404px] mask-size-[1064.89px_1064.89px] mix-blend-overlay right-[53.563%] top-[23.139%]"
        data-name="Element"
        style={{ maskImage: `url('${imgElement1}')` }}
      >
        <div className="absolute inset-[-53.833%]">
          <svg
            className="block size-full"
            fill="none"
            preserveAspectRatio="none"
            viewBox="0 0 1456 1456"
          >
            <g
              filter="url(#filter0_f_1_6705)"
              id="Element"
              style={{ mixBlendMode: "overlay" }}
            >
              <circle
                cx="728.294"
                cy="728.294"
                fill="var(--fill-0, #D74D12)"
                r="350.294"
              />
            </g>
            <defs>
              <filter
                colorInterpolationFilters="sRGB"
                filterUnits="userSpaceOnUse"
                height="1454.89"
                id="filter0_f_1_6705"
                width="1454.89"
                x="0.850647"
                y="0.850647"
              >
                <feFlood floodOpacity="0" result="BackgroundImageFix" />
                <feBlend
                  in="SourceGraphic"
                  in2="BackgroundImageFix"
                  mode="normal"
                  result="shape"
                />
                <feGaussianBlur
                  result="effect1_foregroundBlur_1_6705"
                  stdDeviation="188.575"
                />
              </filter>
            </defs>
          </svg>
        </div>
      </div>
      <div
        className="absolute bottom-[-2.928%] left-[-2.458%] mask-alpha mask-intersect mask-no-clip mask-no-repeat mask-position-[26.1719px_-111.896px] mask-size-[1064.89px_1064.89px] mix-blend-darken right-[4.502%] top-[10.508%]"
        data-name="Element"
        style={{ maskImage: `url('${imgElement1}')` }}
      >
        <div className="absolute bottom-[-13.525%] left-[-12.761%] right-[-12.761%] top-[-13.525%]">
          <svg
            className="block size-full"
            fill="none"
            preserveAspectRatio="none"
            viewBox="0 0 1311 1252"
          >
            <g
              filter="url(#filter0_f_1_6680)"
              id="Element"
              style={{ mixBlendMode: "darken" }}
            >
              <path
                d={svgPaths.p3ad44990}
                fill="var(--fill-0, #AC0CB9)"
                fillOpacity="0.7"
              />
            </g>
            <defs>
              <filter
                colorInterpolationFilters="sRGB"
                filterUnits="userSpaceOnUse"
                height="1250.4"
                id="filter0_f_1_6680"
                width="1309.34"
                x="0.888474"
                y="0.888474"
              >
                <feFlood floodOpacity="0" result="BackgroundImageFix" />
                <feBlend
                  in="SourceGraphic"
                  in2="BackgroundImageFix"
                  mode="normal"
                  result="shape"
                />
                <feGaussianBlur
                  result="effect1_foregroundBlur_1_6680"
                  stdDeviation="66.5558"
                />
              </filter>
            </defs>
          </svg>
        </div>
      </div>
    </div>
  );
}

function BackgroundChat1() {
  return (
    <div
      className="absolute blur-[80.8968px] filter opacity-40 size-[417.96px] top-[186px] translate-x-[-50%]"
      data-name="Background Chat"
      style={{ left: "calc(50% - 0.000473022px)" }}
    >
      <div
        className="absolute inset-0 mask-alpha mask-intersect mask-no-clip mask-no-repeat mask-position-[0px] mask-size-[417.96px_417.96px]"
        data-name="Element"
        style={{ maskImage: `url('${imgElement2}')` }}
      >
        <svg
          className="block size-full"
          fill="none"
          preserveAspectRatio="none"
          viewBox="0 0 418 418"
        >
          <circle
            cx="208.98"
            cy="208.98"
            fill="url(#paint0_radial_1_6582)"
            id="Element"
            r="208.98"
          />
          <defs>
            <radialGradient
              cx="0"
              cy="0"
              gradientTransform="translate(243.039 137.438) rotate(103.201) scale(238.879)"
              gradientUnits="userSpaceOnUse"
              id="paint0_radial_1_6582"
              r="1"
            >
              <stop stopColor="#0679FF" />
              <stop offset="1" stopColor="#2A8CFF" />
            </radialGradient>
          </defs>
        </svg>
      </div>
      <div
        className="absolute bottom-[48.276%] left-[-40.868%] mask-alpha mask-intersect mask-no-clip mask-no-repeat mask-position-[170.813px_163.6px] mask-size-[417.96px_417.96px] right-[50.002%] top-[-39.142%]"
        data-name="Element"
        style={{ maskImage: `url('${imgElement2}')` }}
      >
        <div className="absolute inset-[-32.098%]">
          <svg
            className="block size-full"
            fill="none"
            preserveAspectRatio="none"
            viewBox="0 0 624 624"
          >
            <g filter="url(#filter0_f_1_6577)" id="Element">
              <circle
                cx="311.892"
                cy="311.892"
                fill="var(--fill-0, #5344FE)"
                fillOpacity="0.68"
                r="189.892"
              />
            </g>
            <defs>
              <filter
                colorInterpolationFilters="sRGB"
                filterUnits="userSpaceOnUse"
                height="623.595"
                id="filter0_f_1_6577"
                width="623.595"
                x="0.094986"
                y="0.094986"
              >
                <feFlood floodOpacity="0" result="BackgroundImageFix" />
                <feBlend
                  in="SourceGraphic"
                  in2="BackgroundImageFix"
                  mode="normal"
                  result="shape"
                />
                <feGaussianBlur
                  result="effect1_foregroundBlur_1_6577"
                  stdDeviation="60.9525"
                />
              </filter>
            </defs>
          </svg>
        </div>
      </div>
      <div
        className="absolute bottom-[17.105%] left-[77.849%] mask-alpha mask-intersect mask-no-clip mask-no-repeat mask-position-[-325.378px_-71.4923px] mask-size-[417.96px_417.96px] mix-blend-overlay right-[-43.639%] top-[17.105%]"
        data-name="Element"
        style={{ maskImage: `url('${imgElement2}')` }}
      >
        <div className="absolute inset-[-53.833%]">
          <svg
            className="block size-full"
            fill="none"
            preserveAspectRatio="none"
            viewBox="0 0 572 572"
          >
            <g
              filter="url(#filter0_f_1_6575)"
              id="Element"
              style={{ mixBlendMode: "overlay" }}
            >
              <circle
                cx="286.487"
                cy="286.487"
                fill="var(--fill-0, #FE445A)"
                r="137.487"
              />
            </g>
            <defs>
              <filter
                colorInterpolationFilters="sRGB"
                filterUnits="userSpaceOnUse"
                height="571.029"
                id="filter0_f_1_6575"
                width="571.029"
                x="0.972473"
                y="0.972473"
              >
                <feFlood floodOpacity="0" result="BackgroundImageFix" />
                <feBlend
                  in="SourceGraphic"
                  in2="BackgroundImageFix"
                  mode="normal"
                  result="shape"
                />
                <feGaussianBlur
                  result="effect1_foregroundBlur_1_6575"
                  stdDeviation="74.0138"
                />
              </filter>
            </defs>
          </svg>
        </div>
      </div>
      <div
        className="absolute bottom-[11.072%] left-[-19.352%] mask-alpha mask-intersect mask-no-clip mask-no-repeat mask-position-[80.8837px_-96.7113px] mask-size-[417.96px_417.96px] mix-blend-overlay right-[53.563%] top-[23.139%]"
        data-name="Element"
        style={{ maskImage: `url('${imgElement2}')` }}
      >
        <div className="absolute inset-[-53.833%]">
          <svg
            className="block size-full"
            fill="none"
            preserveAspectRatio="none"
            viewBox="0 0 572 572"
          >
            <g
              filter="url(#filter0_f_1_6694)"
              id="Element"
              style={{ mixBlendMode: "overlay" }}
            >
              <circle
                cx="286.487"
                cy="286.487"
                fill="var(--fill-0, #D74D12)"
                r="137.487"
              />
            </g>
            <defs>
              <filter
                colorInterpolationFilters="sRGB"
                filterUnits="userSpaceOnUse"
                height="571.029"
                id="filter0_f_1_6694"
                width="571.029"
                x="0.972473"
                y="0.972473"
              >
                <feFlood floodOpacity="0" result="BackgroundImageFix" />
                <feBlend
                  in="SourceGraphic"
                  in2="BackgroundImageFix"
                  mode="normal"
                  result="shape"
                />
                <feGaussianBlur
                  result="effect1_foregroundBlur_1_6694"
                  stdDeviation="74.0138"
                />
              </filter>
            </defs>
          </svg>
        </div>
      </div>
      <div
        className="absolute bottom-[-2.928%] left-[-2.458%] mask-alpha mask-intersect mask-no-clip mask-no-repeat mask-position-[10.2722px_-43.9183px] mask-size-[417.96px_417.96px] mix-blend-darken right-[4.502%] top-[10.508%]"
        data-name="Element"
        style={{ maskImage: `url('${imgElement2}')` }}
      >
        <div className="absolute bottom-[-13.525%] left-[-12.761%] right-[-12.761%] top-[-13.525%]">
          <svg
            className="block size-full"
            fill="none"
            preserveAspectRatio="none"
            viewBox="0 0 515 492"
          >
            <g
              filter="url(#filter0_f_1_6659)"
              id="Element"
              style={{ mixBlendMode: "darken" }}
            >
              <path
                d={svgPaths.p1ee2b00}
                fill="var(--fill-0, #AC0CB9)"
                fillOpacity="0.7"
              />
            </g>
            <defs>
              <filter
                colorInterpolationFilters="sRGB"
                filterUnits="userSpaceOnUse"
                height="490.771"
                id="filter0_f_1_6659"
                width="513.905"
                x="0.754993"
                y="0.754993"
              >
                <feFlood floodOpacity="0" result="BackgroundImageFix" />
                <feBlend
                  in="SourceGraphic"
                  in2="BackgroundImageFix"
                  mode="normal"
                  result="shape"
                />
                <feGaussianBlur
                  result="effect1_foregroundBlur_1_6659"
                  stdDeviation="26.1225"
                />
              </filter>
            </defs>
          </svg>
        </div>
      </div>
    </div>
  );
}

function PageTitleWrapper() {
  return (
    <div
      className="box-border content-stretch flex flex-col gap-1.5 items-center justify-start leading-[0] not-italic p-0 relative shrink-0 text-center w-full"
      data-name="Page Title Wrapper"
    >
      <div className="font-['Inter:Medium',_sans-serif] font-medium relative shrink-0 text-[#19213d] text-[22px] text-nowrap">
        <p className="block leading-[1.3] whitespace-pre">
          Welcome back, Mauro
        </p>
      </div>
      <div
        className="font-['Inter:Regular',_sans-serif] font-normal min-w-full relative shrink-0 text-[#666f8d] text-[14px]"
        style={{ width: "min-content" }}
      >
        <p className="block leading-[1.5]">
          This is a sample text for demonstration purposes.
        </p>
      </div>
    </div>
  );
}

function PrompBox() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-2 items-center justify-start p-0 relative shrink-0"
      data-name="Promp box"
    >
      <div className="font-['Inter:Regular',_sans-serif] font-normal leading-[0] not-italic relative shrink-0 text-[#666f8d] text-[14px] text-left text-nowrap">
        <p className="block leading-[1.5] whitespace-pre">
          How can I assist you today?
        </p>
      </div>
    </div>
  );
}

function FilledSend() {
  return (
    <div className="relative shrink-0 size-5" data-name="Filled/Send">
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 20 20"
      >
        <g id="Filled/Send">
          <path
            d={svgPaths.p1850be00}
            fill="var(--fill-0, white)"
            id="Element"
          />
        </g>
      </svg>
    </div>
  );
}

function PrimaryButton2() {
  return (
    <div
      className="bg-gradient-to-b from-[#2b7afb] relative rounded-lg shrink-0 size-[42px] to-[#213bfd] via-100% via-[#2174fd]"
      data-name="Primary Button"
    >
      <div className="box-border content-stretch flex flex-row items-center justify-center overflow-clip p-0 relative size-[42px]">
        <FilledSend />
      </div>
      <div className="absolute inset-0 pointer-events-none shadow-[0px_-2px_0.3px_0px_inset_rgba(14,56,125,0.18),0px_2px_1px_0px_inset_rgba(255,255,255,0.22)]" />
      <div className="absolute border border-[#174bd2] border-solid inset-0 pointer-events-none rounded-lg shadow-[0px_2px_5px_0px_rgba(20,88,201,0.17)]" />
    </div>
  );
}

function PromptBox() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-4 items-center justify-end p-0 relative shrink-0"
      data-name="Prompt Box"
    >
      <PrimaryButton2 />
    </div>
  );
}

function BoxWrapper() {
  return (
    <div
      className="bg-[#ffffff] mb-[-1px] relative rounded-2xl shrink-0 w-full"
      data-name="Box Wrapper"
    >
      <div className="absolute border border-[#f0f2f5] border-solid inset-0 pointer-events-none rounded-2xl shadow-[0px_2px_4px_0px_rgba(25,33,61,0.08)]" />
      <div className="flex flex-row items-center relative size-full">
        <div className="box-border content-stretch flex flex-row items-center justify-between pl-4 pr-2 py-2 relative w-full">
          <PrompBox />
          <PromptBox />
        </div>
      </div>
    </div>
  );
}

function PromptBox1() {
  return (
    <div
      className="box-border content-stretch flex flex-col items-end justify-start pb-px pt-0 px-0 relative shrink-0 w-full"
      data-name="Prompt Box"
    >
      <BoxWrapper />
    </div>
  );
}

function TopPart() {
  return (
    <div
      className="box-border content-stretch flex flex-col gap-6 items-center justify-start max-w-[400px] p-0 relative shrink-0 w-[400px]"
      data-name="Top Part"
    >
      <PageTitleWrapper />
      <PromptBox1 />
    </div>
  );
}

function PromptBox2() {
  return (
    <div
      className="bg-[#ffffff] relative rounded-2xl shrink-0 w-full"
      data-name="Prompt Box"
    >
      <div className="flex flex-col items-center justify-center overflow-clip relative size-full">
        <div className="box-border content-stretch flex flex-col gap-2.5 items-center justify-center px-8 py-12 relative w-full">
          <BackgroundChat1 />
          <TopPart />
        </div>
      </div>
      <div className="absolute border border-[#e3e6ea] border-solid inset-0 pointer-events-none rounded-2xl shadow-[0px_2px_4px_0px_rgba(25,33,61,0.08)]" />
    </div>
  );
}

function LineRoundedSearch2() {
  return (
    <div
      className="relative shrink-0 size-[13px]"
      data-name="Line Rounded/Search"
    >
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 13 13"
      >
        <g id="Line Rounded/Search">
          <path
            d={svgPaths.p37632600}
            id="Element"
            stroke="var(--stroke-0, #666F8D)"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="1.2"
          />
        </g>
      </svg>
    </div>
  );
}

function PlaceholderWrapper2() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-1 items-center justify-start p-0 relative shrink-0"
      data-name="Placeholder Wrapper"
    >
      <LineRoundedSearch2 />
      <div className="font-['Inter:Regular',_sans-serif] font-normal leading-[0] not-italic relative shrink-0 text-[#666f8d] text-[12px] text-left text-nowrap">
        <p className="block leading-[1.3] whitespace-pre">
          Search for conversations...
        </p>
      </div>
    </div>
  );
}

function InputText2() {
  return (
    <div
      className="bg-[#ffffff] box-border content-stretch flex flex-row h-10 items-center justify-start min-h-[39px] pl-3 pr-1.5 py-1.5 relative rounded-lg shrink-0 w-[266px]"
      data-name="Input Text"
    >
      <div className="absolute border border-[#f0f2f5] border-solid inset-0 pointer-events-none rounded-lg shadow-[0px_1px_3px_0px_rgba(25,33,61,0.1)]" />
      <PlaceholderWrapper2 />
    </div>
  );
}

function LineRoundedChip() {
  return (
    <div className="relative shrink-0 size-3" data-name="Line Rounded/Chip">
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 12 12"
      >
        <g id="Line Rounded/Chip">
          <path
            d={svgPaths.p2ad5e900}
            id="Vector"
            stroke="var(--stroke-0, #666F8D)"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="0.72"
          />
        </g>
      </svg>
    </div>
  );
}

function PlaceholderWrapper3() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-1.5 items-center justify-start p-0 relative shrink-0"
      data-name="Placeholder Wrapper"
    >
      <LineRoundedChip />
      <div className="font-['Inter:Regular',_sans-serif] font-normal leading-[0] not-italic relative shrink-0 text-[#666f8d] text-[12px] text-left text-nowrap">
        <p className="block leading-[1.3] whitespace-pre">Model Type</p>
      </div>
    </div>
  );
}

function LineRoundedChevronDown() {
  return (
    <div
      className="relative shrink-0 size-3.5"
      data-name="Line Rounded/Chevron down"
    >
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 14 14"
      >
        <g id="Line Rounded/Chevron down">
          <path
            d={svgPaths.p2fd69c00}
            id="Element"
            stroke="var(--stroke-0, #666F8D)"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="1.3"
          />
        </g>
      </svg>
    </div>
  );
}

function Select() {
  return (
    <div
      className="bg-[#ffffff] box-border content-stretch flex flex-row items-center justify-between min-h-10 px-3 py-1.5 relative rounded-lg shrink-0 w-[146px]"
      data-name="Select"
    >
      <div className="absolute border border-[#f0f2f5] border-solid inset-0 pointer-events-none rounded-lg shadow-[0px_1px_3px_0px_rgba(25,33,61,0.1)]" />
      <PlaceholderWrapper3 />
      <LineRoundedChevronDown />
    </div>
  );
}

function LineRoundedFilters() {
  return (
    <div className="relative shrink-0 size-3" data-name="Line Rounded/Filters">
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 12 12"
      >
        <g id="Line Rounded/Filters">
          <g id="Element">
            <mask fill="white" id="path-1-inside-1_1_6528">
              <path d={svgPaths.p3f4a7500} />
              <path d={svgPaths.p27b6a880} />
              <path d={svgPaths.p6d43800} />
            </mask>
            <path
              d={svgPaths.p1519c800}
              fill="var(--stroke-0, #666F8D)"
              mask="url(#path-1-inside-1_1_6528)"
            />
          </g>
        </g>
      </svg>
    </div>
  );
}

function PlaceholderWrapper4() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-1.5 items-center justify-start p-0 relative shrink-0"
      data-name="Placeholder Wrapper"
    >
      <LineRoundedFilters />
      <div className="font-['Inter:Regular',_sans-serif] font-normal leading-[0] not-italic relative shrink-0 text-[#666f8d] text-[12px] text-left text-nowrap">
        <p className="block leading-[1.3] whitespace-pre">Arrange by</p>
      </div>
    </div>
  );
}

function LineRoundedChevronDown1() {
  return (
    <div
      className="relative shrink-0 size-3.5"
      data-name="Line Rounded/Chevron down"
    >
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 14 14"
      >
        <g id="Line Rounded/Chevron down">
          <path
            d={svgPaths.p2fd69c00}
            id="Element"
            stroke="var(--stroke-0, #666F8D)"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="1.3"
          />
        </g>
      </svg>
    </div>
  );
}

function Select1() {
  return (
    <div
      className="bg-[#ffffff] box-border content-stretch flex flex-row items-center justify-between min-h-10 px-3 py-1.5 relative rounded-lg shrink-0 w-[146px]"
      data-name="Select"
    >
      <div className="absolute border border-[#f0f2f5] border-solid inset-0 pointer-events-none rounded-lg shadow-[0px_1px_3px_0px_rgba(25,33,61,0.1)]" />
      <PlaceholderWrapper4 />
      <LineRoundedChevronDown1 />
    </div>
  );
}

function RightSide() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-2 items-start justify-start p-0 relative shrink-0"
      data-name="Right Side"
    >
      <InputText2 />
      <Select />
      <Select1 />
    </div>
  );
}

function TitleSearchWrapper() {
  return (
    <div
      className="box-border content-stretch flex flex-row items-center justify-between p-0 relative shrink-0 w-full"
      data-name="Title & Search Wrapper"
    >
      <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#666f8d] text-[16px] text-left text-nowrap">
        <p className="block leading-[1.3] whitespace-pre">Conversations (56)</p>
      </div>
      <RightSide />
    </div>
  );
}

function Badge6() {
  return (
    <div
      className="bg-[#f7f8fa] box-border content-stretch flex flex-row gap-1 items-center justify-center p-[4px] relative rounded shadow-[0px_1px_3px_0px_rgba(25,33,61,0.1)] shrink-0"
      data-name="Badge"
    >
      <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#19213d] text-[12px] text-center text-nowrap">
        <p className="block leading-[1.3] whitespace-pre">GPT 4</p>
      </div>
    </div>
  );
}

function Icon() {
  return (
    <div className="relative shrink-0 size-3.5" data-name="Icon">
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 14 14"
      >
        <g id="Icon">
          <path
            d={svgPaths.p1c44a500}
            id="Element"
            stroke="var(--stroke-0, #666F8D)"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="1.3"
          />
        </g>
      </svg>
    </div>
  );
}

function TextIcon() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-1 items-center justify-end min-w-10 p-0 relative shrink-0 w-10"
      data-name="Text Icon"
    >
      <Icon />
      <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#666f8d] text-[12px] text-left text-nowrap">
        <p className="block leading-[1.3] whitespace-pre">30</p>
      </div>
    </div>
  );
}

function Icon1() {
  return (
    <div className="relative shrink-0 size-3.5" data-name="Icon">
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 14 14"
      >
        <g id="Icon">
          <path
            d={svgPaths.p27ec8c00}
            id="Element"
            stroke="var(--stroke-0, #666F8D)"
            strokeLinecap="round"
            strokeWidth="1.3"
          />
        </g>
      </svg>
    </div>
  );
}

function TextIcon1() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-1 items-center justify-end min-w-20 p-0 relative shrink-0 w-20"
      data-name="Text Icon"
    >
      <Icon1 />
      <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#666f8d] text-[12px] text-left text-nowrap">
        <p className="block leading-[1.3] whitespace-pre">Just now</p>
      </div>
    </div>
  );
}

function Element18() {
  return (
    <div
      className="absolute bottom-[4.642%] left-[44.96%] right-[44.959%] top-[4.642%]"
      data-name="Element"
    >
      <div className="absolute bottom-[-5.118%] left-[-46.058%] right-[-46.067%] top-[-5.118%]">
        <svg
          className="block size-full"
          fill="none"
          preserveAspectRatio="none"
          viewBox="0 0 4 15"
        >
          <g id="Element">
            <path
              d={svgPaths.p2438d7c0}
              id="Element_2"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.p2e9b9800}
              id="Element_3"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.p13d67a00}
              id="Element_4"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.pae45800}
              id="Element_5"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.p4f938c0}
              id="Element_6"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.p1590a680}
              id="Element_7"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
          </g>
        </svg>
      </div>
    </div>
  );
}

function LineRoundedDots() {
  return (
    <div className="relative shrink-0 size-3.5" data-name="Line Rounded/Dots">
      <Element18 />
    </div>
  );
}

function RightSide1() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-6 items-center justify-start p-0 relative shrink-0"
      data-name="Right Side"
    >
      <Badge6 />
      <TextIcon />
      <TextIcon1 />
      <LineRoundedDots />
    </div>
  );
}

function ChatHistory() {
  return (
    <div
      className="bg-[#ffffff] relative rounded-lg shrink-0 w-full"
      data-name="Chat history"
    >
      <div className="flex flex-row items-center overflow-clip relative size-full">
        <div className="box-border content-stretch flex flex-row items-center justify-between px-6 py-4 relative w-full">
          <div className="basis-0 font-['Inter:Medium',_sans-serif] font-medium grow leading-[0] min-h-px min-w-px not-italic overflow-ellipsis overflow-hidden relative shrink-0 text-[#19213d] text-[14px] text-left text-nowrap">
            <p className="[text-overflow:inherit] [text-wrap-mode:inherit]\' [white-space-collapse:inherit] block leading-[1.3] overflow-inherit">
              This text serves as an example of practical content.
            </p>
          </div>
          <RightSide1 />
        </div>
      </div>
      <div className="absolute border border-[#e3e6ea] border-solid inset-0 pointer-events-none rounded-lg shadow-[0px_2px_4px_0px_rgba(25,33,61,0.08)]" />
    </div>
  );
}

function Badge7() {
  return (
    <div
      className="bg-[#f7f8fa] box-border content-stretch flex flex-row gap-1 items-center justify-center p-[4px] relative rounded shadow-[0px_1px_3px_0px_rgba(25,33,61,0.1)] shrink-0"
      data-name="Badge"
    >
      <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#19213d] text-[12px] text-center text-nowrap">
        <p className="block leading-[1.3] whitespace-pre">Llama 2</p>
      </div>
    </div>
  );
}

function Icon2() {
  return (
    <div className="relative shrink-0 size-3.5" data-name="Icon">
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 14 14"
      >
        <g id="Icon">
          <path
            d={svgPaths.p1c44a500}
            id="Element"
            stroke="var(--stroke-0, #666F8D)"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="1.3"
          />
        </g>
      </svg>
    </div>
  );
}

function TextIcon2() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-1 items-center justify-end min-w-10 p-0 relative shrink-0 w-10"
      data-name="Text Icon"
    >
      <Icon2 />
      <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#666f8d] text-[12px] text-left text-nowrap">
        <p className="block leading-[1.3] whitespace-pre">15</p>
      </div>
    </div>
  );
}

function Icon3() {
  return (
    <div className="relative shrink-0 size-3.5" data-name="Icon">
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 14 14"
      >
        <g id="Icon">
          <path
            d={svgPaths.p27ec8c00}
            id="Element"
            stroke="var(--stroke-0, #666F8D)"
            strokeLinecap="round"
            strokeWidth="1.3"
          />
        </g>
      </svg>
    </div>
  );
}

function TextIcon3() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-1 items-center justify-end min-w-20 p-0 relative shrink-0 w-20"
      data-name="Text Icon"
    >
      <Icon3 />
      <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#666f8d] text-[12px] text-left text-nowrap">
        <p className="block leading-[1.3] whitespace-pre">5 minutes ago</p>
      </div>
    </div>
  );
}

function Element19() {
  return (
    <div
      className="absolute bottom-[4.642%] left-[44.96%] right-[44.959%] top-[4.641%]"
      data-name="Element"
    >
      <div className="absolute bottom-[-5.118%] left-[-46.058%] right-[-46.067%] top-[-5.118%]">
        <svg
          className="block size-full"
          fill="none"
          preserveAspectRatio="none"
          viewBox="0 0 4 15"
        >
          <g id="Element">
            <path
              d={svgPaths.p2438d7c0}
              id="Element_2"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.p11754f20}
              id="Element_3"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.p243dbb00}
              id="Element_4"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.p3839b00}
              id="Element_5"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.p2df72780}
              id="Element_6"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.p846ecdc}
              id="Element_7"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
          </g>
        </svg>
      </div>
    </div>
  );
}

function LineRoundedDots1() {
  return (
    <div className="relative shrink-0 size-3.5" data-name="Line Rounded/Dots">
      <Element19 />
    </div>
  );
}

function RightSide2() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-6 items-center justify-start p-0 relative shrink-0"
      data-name="Right Side"
    >
      <Badge7 />
      <TextIcon2 />
      <TextIcon3 />
      <LineRoundedDots1 />
    </div>
  );
}

function ChatHistory1() {
  return (
    <div
      className="bg-[#ffffff] relative rounded-lg shrink-0 w-full"
      data-name="Chat history"
    >
      <div className="flex flex-row items-center overflow-clip relative size-full">
        <div className="box-border content-stretch flex flex-row items-center justify-between px-6 py-4 relative w-full">
          <div className="basis-0 font-['Inter:Medium',_sans-serif] font-medium grow leading-[0] min-h-px min-w-px not-italic overflow-ellipsis overflow-hidden relative shrink-0 text-[#19213d] text-[14px] text-left text-nowrap">
            <p className="[text-overflow:inherit] [text-wrap-mode:inherit]\' [white-space-collapse:inherit] block leading-[1.3] overflow-inherit">
              An unexpected error has occurred.
            </p>
          </div>
          <RightSide2 />
        </div>
      </div>
      <div className="absolute border border-[#e3e6ea] border-solid inset-0 pointer-events-none rounded-lg shadow-[0px_2px_4px_0px_rgba(25,33,61,0.08)]" />
    </div>
  );
}

function Badge8() {
  return (
    <div
      className="bg-[#f7f8fa] box-border content-stretch flex flex-row gap-1 items-center justify-center p-[4px] relative rounded shadow-[0px_1px_3px_0px_rgba(25,33,61,0.1)] shrink-0"
      data-name="Badge"
    >
      <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#19213d] text-[12px] text-center text-nowrap">
        <p className="block leading-[1.3] whitespace-pre">Mistral 8x7B</p>
      </div>
    </div>
  );
}

function Icon4() {
  return (
    <div className="relative shrink-0 size-3.5" data-name="Icon">
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 14 14"
      >
        <g id="Icon">
          <path
            d={svgPaths.p1c44a500}
            id="Element"
            stroke="var(--stroke-0, #666F8D)"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="1.3"
          />
        </g>
      </svg>
    </div>
  );
}

function TextIcon4() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-1 items-center justify-end min-w-10 p-0 relative shrink-0 w-10"
      data-name="Text Icon"
    >
      <Icon4 />
      <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#666f8d] text-[12px] text-left text-nowrap">
        <p className="block leading-[1.3] whitespace-pre">10</p>
      </div>
    </div>
  );
}

function Icon5() {
  return (
    <div className="relative shrink-0 size-3.5" data-name="Icon">
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 14 14"
      >
        <g id="Icon">
          <path
            d={svgPaths.p27ec8c00}
            id="Element"
            stroke="var(--stroke-0, #666F8D)"
            strokeLinecap="round"
            strokeWidth="1.3"
          />
        </g>
      </svg>
    </div>
  );
}

function TextIcon5() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-1 items-center justify-end min-w-20 p-0 relative shrink-0 w-20"
      data-name="Text Icon"
    >
      <Icon5 />
      <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#666f8d] text-[12px] text-left text-nowrap">
        <p className="block leading-[1.3] whitespace-pre">22 minutes ago</p>
      </div>
    </div>
  );
}

function Element20() {
  return (
    <div
      className="absolute bottom-[4.642%] left-[44.96%] right-[44.959%] top-[4.641%]"
      data-name="Element"
    >
      <div className="absolute bottom-[-5.118%] left-[-46.058%] right-[-46.067%] top-[-5.118%]">
        <svg
          className="block size-full"
          fill="none"
          preserveAspectRatio="none"
          viewBox="0 0 4 15"
        >
          <g id="Element">
            <path
              d={svgPaths.p2438d7c0}
              id="Element_2"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.p11754f20}
              id="Element_3"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.p243dbb00}
              id="Element_4"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.p3839b00}
              id="Element_5"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.p2df72780}
              id="Element_6"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.p846ecdc}
              id="Element_7"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
          </g>
        </svg>
      </div>
    </div>
  );
}

function LineRoundedDots2() {
  return (
    <div className="relative shrink-0 size-3.5" data-name="Line Rounded/Dots">
      <Element20 />
    </div>
  );
}

function RightSide3() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-6 items-center justify-start p-0 relative shrink-0"
      data-name="Right Side"
    >
      <Badge8 />
      <TextIcon4 />
      <TextIcon5 />
      <LineRoundedDots2 />
    </div>
  );
}

function ChatHistory2() {
  return (
    <div
      className="bg-[#ffffff] relative rounded-lg shrink-0 w-full"
      data-name="Chat history"
    >
      <div className="flex flex-row items-center overflow-clip relative size-full">
        <div className="box-border content-stretch flex flex-row items-center justify-between px-6 py-4 relative w-full">
          <div className="basis-0 font-['Inter:Medium',_sans-serif] font-medium grow leading-[0] min-h-px min-w-px not-italic overflow-ellipsis overflow-hidden relative shrink-0 text-[#19213d] text-[14px] text-left text-nowrap">
            <p className="[text-overflow:inherit] [text-wrap-mode:inherit]\' [white-space-collapse:inherit] block leading-[1.3] overflow-inherit">
              The system is currently under maintenance.
            </p>
          </div>
          <RightSide3 />
        </div>
      </div>
      <div className="absolute border border-[#e3e6ea] border-solid inset-0 pointer-events-none rounded-lg shadow-[0px_2px_4px_0px_rgba(25,33,61,0.08)]" />
    </div>
  );
}

function Badge9() {
  return (
    <div
      className="bg-[#f7f8fa] box-border content-stretch flex flex-row gap-1 items-center justify-center p-[4px] relative rounded shadow-[0px_1px_3px_0px_rgba(25,33,61,0.1)] shrink-0"
      data-name="Badge"
    >
      <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#19213d] text-[12px] text-center text-nowrap">
        <p className="block leading-[1.3] whitespace-pre">GPT 3.5</p>
      </div>
    </div>
  );
}

function Icon6() {
  return (
    <div className="relative shrink-0 size-3.5" data-name="Icon">
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 14 14"
      >
        <g id="Icon">
          <path
            d={svgPaths.p1c44a500}
            id="Element"
            stroke="var(--stroke-0, #666F8D)"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="1.3"
          />
        </g>
      </svg>
    </div>
  );
}

function TextIcon6() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-1 items-center justify-end min-w-10 p-0 relative shrink-0 w-10"
      data-name="Text Icon"
    >
      <Icon6 />
      <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#666f8d] text-[12px] text-left text-nowrap">
        <p className="block leading-[1.3] whitespace-pre">25</p>
      </div>
    </div>
  );
}

function Icon7() {
  return (
    <div className="relative shrink-0 size-3.5" data-name="Icon">
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 14 14"
      >
        <g id="Icon">
          <path
            d={svgPaths.p27ec8c00}
            id="Element"
            stroke="var(--stroke-0, #666F8D)"
            strokeLinecap="round"
            strokeWidth="1.3"
          />
        </g>
      </svg>
    </div>
  );
}

function TextIcon7() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-1 items-center justify-end min-w-20 p-0 relative shrink-0 w-20"
      data-name="Text Icon"
    >
      <Icon7 />
      <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#666f8d] text-[12px] text-left text-nowrap">
        <p className="block leading-[1.3] whitespace-pre">1 hour ago</p>
      </div>
    </div>
  );
}

function Element21() {
  return (
    <div
      className="absolute bottom-[4.642%] left-[44.96%] right-[44.959%] top-[4.641%]"
      data-name="Element"
    >
      <div className="absolute bottom-[-5.118%] left-[-46.058%] right-[-46.067%] top-[-5.118%]">
        <svg
          className="block size-full"
          fill="none"
          preserveAspectRatio="none"
          viewBox="0 0 4 15"
        >
          <g id="Element">
            <path
              d={svgPaths.p2438d7c0}
              id="Element_2"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.p11754f20}
              id="Element_3"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.p243dbb00}
              id="Element_4"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.p3839b00}
              id="Element_5"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.p2df72780}
              id="Element_6"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.p846ecdc}
              id="Element_7"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
          </g>
        </svg>
      </div>
    </div>
  );
}

function LineRoundedDots3() {
  return (
    <div className="relative shrink-0 size-3.5" data-name="Line Rounded/Dots">
      <Element21 />
    </div>
  );
}

function RightSide4() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-6 items-center justify-start p-0 relative shrink-0"
      data-name="Right Side"
    >
      <Badge9 />
      <TextIcon6 />
      <TextIcon7 />
      <LineRoundedDots3 />
    </div>
  );
}

function ChatHistory3() {
  return (
    <div
      className="bg-[#ffffff] relative rounded-lg shrink-0 w-full"
      data-name="Chat history"
    >
      <div className="flex flex-row items-center overflow-clip relative size-full">
        <div className="box-border content-stretch flex flex-row items-center justify-between px-6 py-4 relative w-full">
          <div className="basis-0 font-['Inter:Medium',_sans-serif] font-medium grow leading-[0] min-h-px min-w-px not-italic overflow-ellipsis overflow-hidden relative shrink-0 text-[#19213d] text-[14px] text-left text-nowrap">
            <p className="[text-overflow:inherit] [text-wrap-mode:inherit]\' [white-space-collapse:inherit] block leading-[1.3] overflow-inherit">
              Your request is being processed.
            </p>
          </div>
          <RightSide4 />
        </div>
      </div>
      <div className="absolute border border-[#e3e6ea] border-solid inset-0 pointer-events-none rounded-lg shadow-[0px_2px_4px_0px_rgba(25,33,61,0.08)]" />
    </div>
  );
}

function Badge10() {
  return (
    <div
      className="bg-[#f7f8fa] box-border content-stretch flex flex-row gap-1 items-center justify-center p-[4px] relative rounded shadow-[0px_1px_3px_0px_rgba(25,33,61,0.1)] shrink-0"
      data-name="Badge"
    >
      <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#19213d] text-[12px] text-center text-nowrap">
        <p className="block leading-[1.3] whitespace-pre">GPT 4</p>
      </div>
    </div>
  );
}

function Icon8() {
  return (
    <div className="relative shrink-0 size-3.5" data-name="Icon">
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 14 14"
      >
        <g id="Icon">
          <path
            d={svgPaths.p1c44a500}
            id="Element"
            stroke="var(--stroke-0, #666F8D)"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="1.3"
          />
        </g>
      </svg>
    </div>
  );
}

function TextIcon8() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-1 items-center justify-end min-w-10 p-0 relative shrink-0 w-10"
      data-name="Text Icon"
    >
      <Icon8 />
      <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#666f8d] text-[12px] text-left text-nowrap">
        <p className="block leading-[1.3] whitespace-pre">30</p>
      </div>
    </div>
  );
}

function Icon9() {
  return (
    <div className="relative shrink-0 size-3.5" data-name="Icon">
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 14 14"
      >
        <g id="Icon">
          <path
            d={svgPaths.p27ec8c00}
            id="Element"
            stroke="var(--stroke-0, #666F8D)"
            strokeLinecap="round"
            strokeWidth="1.3"
          />
        </g>
      </svg>
    </div>
  );
}

function TextIcon9() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-1 items-center justify-end min-w-20 p-0 relative shrink-0 w-20"
      data-name="Text Icon"
    >
      <Icon9 />
      <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#666f8d] text-[12px] text-left text-nowrap">
        <p className="block leading-[1.3] whitespace-pre">2 hours ago</p>
      </div>
    </div>
  );
}

function Element22() {
  return (
    <div
      className="absolute bottom-[4.642%] left-[44.96%] right-[44.959%] top-[4.641%]"
      data-name="Element"
    >
      <div className="absolute bottom-[-5.118%] left-[-46.058%] right-[-46.067%] top-[-5.118%]">
        <svg
          className="block size-full"
          fill="none"
          preserveAspectRatio="none"
          viewBox="0 0 4 15"
        >
          <g id="Element">
            <path
              d={svgPaths.p2438d7c0}
              id="Element_2"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.p11754f20}
              id="Element_3"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.p243dbb00}
              id="Element_4"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.p3839b00}
              id="Element_5"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.p2df72780}
              id="Element_6"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.p846ecdc}
              id="Element_7"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
          </g>
        </svg>
      </div>
    </div>
  );
}

function LineRoundedDots4() {
  return (
    <div className="relative shrink-0 size-3.5" data-name="Line Rounded/Dots">
      <Element22 />
    </div>
  );
}

function RightSide5() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-6 items-center justify-start p-0 relative shrink-0"
      data-name="Right Side"
    >
      <Badge10 />
      <TextIcon8 />
      <TextIcon9 />
      <LineRoundedDots4 />
    </div>
  );
}

function ChatHistory4() {
  return (
    <div
      className="bg-[#ffffff] relative rounded-lg shrink-0 w-full"
      data-name="Chat history"
    >
      <div className="flex flex-row items-center overflow-clip relative size-full">
        <div className="box-border content-stretch flex flex-row items-center justify-between px-6 py-4 relative w-full">
          <div className="basis-0 font-['Inter:Medium',_sans-serif] font-medium grow leading-[0] min-h-px min-w-px not-italic overflow-ellipsis overflow-hidden relative shrink-0 text-[#19213d] text-[14px] text-left text-nowrap">
            <p className="[text-overflow:inherit] [text-wrap-mode:inherit]\' [white-space-collapse:inherit] block leading-[1.3] overflow-inherit">
              Please ensure your settings are correct.
            </p>
          </div>
          <RightSide5 />
        </div>
      </div>
      <div className="absolute border border-[#e3e6ea] border-solid inset-0 pointer-events-none rounded-lg shadow-[0px_2px_4px_0px_rgba(25,33,61,0.08)]" />
    </div>
  );
}

function Badge11() {
  return (
    <div
      className="bg-[#f7f8fa] box-border content-stretch flex flex-row gap-1 items-center justify-center p-[4px] relative rounded shadow-[0px_1px_3px_0px_rgba(25,33,61,0.1)] shrink-0"
      data-name="Badge"
    >
      <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#19213d] text-[12px] text-center text-nowrap">
        <p className="block leading-[1.3] whitespace-pre">Llama 2</p>
      </div>
    </div>
  );
}

function Icon10() {
  return (
    <div className="relative shrink-0 size-3.5" data-name="Icon">
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 14 14"
      >
        <g id="Icon">
          <path
            d={svgPaths.p1c44a500}
            id="Element"
            stroke="var(--stroke-0, #666F8D)"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="1.3"
          />
        </g>
      </svg>
    </div>
  );
}

function TextIcon10() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-1 items-center justify-end min-w-10 p-0 relative shrink-0 w-10"
      data-name="Text Icon"
    >
      <Icon10 />
      <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#666f8d] text-[12px] text-left text-nowrap">
        <p className="block leading-[1.3] whitespace-pre">9</p>
      </div>
    </div>
  );
}

function Icon11() {
  return (
    <div className="relative shrink-0 size-3.5" data-name="Icon">
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 14 14"
      >
        <g id="Icon">
          <path
            d={svgPaths.p27ec8c00}
            id="Element"
            stroke="var(--stroke-0, #666F8D)"
            strokeLinecap="round"
            strokeWidth="1.3"
          />
        </g>
      </svg>
    </div>
  );
}

function TextIcon11() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-1 items-center justify-end min-w-20 p-0 relative shrink-0 w-20"
      data-name="Text Icon"
    >
      <Icon11 />
      <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#666f8d] text-[12px] text-left text-nowrap">
        <p className="block leading-[1.3] whitespace-pre">2 hours ago</p>
      </div>
    </div>
  );
}

function Element23() {
  return (
    <div
      className="absolute bottom-[4.642%] left-[44.96%] right-[44.959%] top-[4.641%]"
      data-name="Element"
    >
      <div className="absolute bottom-[-5.118%] left-[-46.058%] right-[-46.067%] top-[-5.118%]">
        <svg
          className="block size-full"
          fill="none"
          preserveAspectRatio="none"
          viewBox="0 0 4 15"
        >
          <g id="Element">
            <path
              d={svgPaths.p2438d7c0}
              id="Element_2"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.p11754f20}
              id="Element_3"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.p243dbb00}
              id="Element_4"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.p3839b00}
              id="Element_5"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.p2df72780}
              id="Element_6"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.p846ecdc}
              id="Element_7"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
          </g>
        </svg>
      </div>
    </div>
  );
}

function LineRoundedDots5() {
  return (
    <div className="relative shrink-0 size-3.5" data-name="Line Rounded/Dots">
      <Element23 />
    </div>
  );
}

function RightSide6() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-6 items-center justify-start p-0 relative shrink-0"
      data-name="Right Side"
    >
      <Badge11 />
      <TextIcon10 />
      <TextIcon11 />
      <LineRoundedDots5 />
    </div>
  );
}

function ChatHistory5() {
  return (
    <div
      className="bg-[#ffffff] relative rounded-lg shrink-0 w-full"
      data-name="Chat history"
    >
      <div className="flex flex-row items-center overflow-clip relative size-full">
        <div className="box-border content-stretch flex flex-row items-center justify-between px-6 py-4 relative w-full">
          <div className="basis-0 font-['Inter:Medium',_sans-serif] font-medium grow leading-[0] min-h-px min-w-px not-italic overflow-ellipsis overflow-hidden relative shrink-0 text-[#19213d] text-[14px] text-left text-nowrap">
            <p className="[text-overflow:inherit] [text-wrap-mode:inherit]\' [white-space-collapse:inherit] block leading-[1.3] overflow-inherit">
              This section is for important announcements.
            </p>
          </div>
          <RightSide6 />
        </div>
      </div>
      <div className="absolute border border-[#e3e6ea] border-solid inset-0 pointer-events-none rounded-lg shadow-[0px_2px_4px_0px_rgba(25,33,61,0.08)]" />
    </div>
  );
}

function Badge12() {
  return (
    <div
      className="bg-[#f7f8fa] box-border content-stretch flex flex-row gap-1 items-center justify-center p-[4px] relative rounded shadow-[0px_1px_3px_0px_rgba(25,33,61,0.1)] shrink-0"
      data-name="Badge"
    >
      <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#19213d] text-[12px] text-center text-nowrap">
        <p className="block leading-[1.3] whitespace-pre">Mistral 7B</p>
      </div>
    </div>
  );
}

function Icon12() {
  return (
    <div className="relative shrink-0 size-3.5" data-name="Icon">
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 14 14"
      >
        <g id="Icon">
          <path
            d={svgPaths.p1c44a500}
            id="Element"
            stroke="var(--stroke-0, #666F8D)"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="1.3"
          />
        </g>
      </svg>
    </div>
  );
}

function TextIcon12() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-1 items-center justify-end min-w-10 p-0 relative shrink-0 w-10"
      data-name="Text Icon"
    >
      <Icon12 />
      <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#666f8d] text-[12px] text-left text-nowrap">
        <p className="block leading-[1.3] whitespace-pre">15</p>
      </div>
    </div>
  );
}

function Icon13() {
  return (
    <div className="relative shrink-0 size-3.5" data-name="Icon">
      <svg
        className="block size-full"
        fill="none"
        preserveAspectRatio="none"
        viewBox="0 0 14 14"
      >
        <g id="Icon">
          <path
            d={svgPaths.p27ec8c00}
            id="Element"
            stroke="var(--stroke-0, #666F8D)"
            strokeLinecap="round"
            strokeWidth="1.3"
          />
        </g>
      </svg>
    </div>
  );
}

function TextIcon13() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-1 items-center justify-end min-w-20 p-0 relative shrink-0 w-20"
      data-name="Text Icon"
    >
      <Icon13 />
      <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#666f8d] text-[12px] text-left text-nowrap">
        <p className="block leading-[1.3] whitespace-pre">3 hours ago.</p>
      </div>
    </div>
  );
}

function Element24() {
  return (
    <div
      className="absolute bottom-[4.642%] left-[44.96%] right-[44.959%] top-[4.641%]"
      data-name="Element"
    >
      <div className="absolute bottom-[-5.118%] left-[-46.058%] right-[-46.067%] top-[-5.118%]">
        <svg
          className="block size-full"
          fill="none"
          preserveAspectRatio="none"
          viewBox="0 0 4 15"
        >
          <g id="Element">
            <path
              d={svgPaths.p2438d7c0}
              id="Element_2"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.p11754f20}
              id="Element_3"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.p243dbb00}
              id="Element_4"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.p3839b00}
              id="Element_5"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.p2df72780}
              id="Element_6"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
            <path
              d={svgPaths.p846ecdc}
              id="Element_7"
              stroke="var(--stroke-0, #666F8D)"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.3"
            />
          </g>
        </svg>
      </div>
    </div>
  );
}

function LineRoundedDots6() {
  return (
    <div className="relative shrink-0 size-3.5" data-name="Line Rounded/Dots">
      <Element24 />
    </div>
  );
}

function RightSide7() {
  return (
    <div
      className="box-border content-stretch flex flex-row gap-6 items-center justify-start p-0 relative shrink-0"
      data-name="Right Side"
    >
      <Badge12 />
      <TextIcon12 />
      <TextIcon13 />
      <LineRoundedDots6 />
    </div>
  );
}

function ChatHistory6() {
  return (
    <div
      className="bg-[#ffffff] relative rounded-lg shrink-0 w-full"
      data-name="Chat history"
    >
      <div className="flex flex-row items-center overflow-clip relative size-full">
        <div className="box-border content-stretch flex flex-row items-center justify-between px-6 py-4 relative w-full">
          <div className="basis-0 font-['Inter:Medium',_sans-serif] font-medium grow leading-[0] min-h-px min-w-px not-italic overflow-ellipsis overflow-hidden relative shrink-0 text-[#19213d] text-[14px] text-left text-nowrap">
            <p className="[text-overflow:inherit] [text-wrap-mode:inherit]\' [white-space-collapse:inherit] block leading-[1.3] overflow-inherit">
              This area contains frequently asked questions.
            </p>
          </div>
          <RightSide7 />
        </div>
      </div>
      <div className="absolute border border-[#e3e6ea] border-solid inset-0 pointer-events-none rounded-lg shadow-[0px_2px_4px_0px_rgba(25,33,61,0.08)]" />
    </div>
  );
}

function ChatsGrid() {
  return (
    <div
      className="box-border content-stretch flex flex-col gap-3 items-start justify-start p-0 relative shrink-0 w-full"
      data-name="Chats Grid"
    >
      <ChatHistory />
      <ChatHistory1 />
      <ChatHistory2 />
      <ChatHistory3 />
      <ChatHistory4 />
      <ChatHistory5 />
      <ChatHistory6 />
    </div>
  );
}

function ChatsWrapper() {
  return (
    <div
      className="box-border content-stretch flex flex-col gap-[30px] items-start justify-start p-0 relative shrink-0 w-full"
      data-name="Chats Wrapper"
    >
      <TitleSearchWrapper />
      <ChatsGrid />
    </div>
  );
}

function ContainerDefault() {
  return (
    <div
      className="basis-0 box-border content-stretch flex flex-col gap-10 grow items-start justify-start min-h-px min-w-px p-0 relative shrink-0"
      data-name="Container Default"
    >
      <PromptBox2 />
      <ChatsWrapper />
    </div>
  );
}

function ChatBodyWrapper() {
  return (
    <div className="relative shrink-0 w-full" data-name="Chat Body Wrapper">
      <div className="flex flex-row justify-center relative size-full">
        <div className="box-border content-stretch flex flex-row items-start justify-center px-[180px] py-10 relative w-full">
          <BackgroundChat />
          <ContainerDefault />
        </div>
      </div>
    </div>
  );
}

function MainBodyWrapper() {
  return (
    <div
      className="basis-0 bg-[#ffffff] grow min-h-px min-w-px relative rounded-2xl self-stretch shrink-0"
      data-name="Main Body Wrapper"
    >
      <div className="box-border content-stretch flex flex-col items-start justify-start overflow-clip p-0 relative size-full">
        <TopBarWrapper />
        <ChatBodyWrapper />
      </div>
      <div className="absolute border border-[#f0f2f5] border-solid inset-0 pointer-events-none rounded-2xl shadow-[0px_1px_3px_0px_rgba(25,33,61,0.1)]" />
    </div>
  );
}

export default function ChatsLayoutV1() {
  return (
    <div
      className="bg-[#f7f8fa] relative rounded-2xl size-full"
      data-name="Chats - Layout V1"
    >
      <div className="relative size-full">
        <div className="box-border content-stretch flex flex-row items-start justify-start overflow-clip pl-0 pr-2.5 py-2.5 relative size-full">
          <SidebarWrapper />
          <MainBodyWrapper />
        </div>
      </div>
    </div>
  );
}